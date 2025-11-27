import os,io,tempfile,traceback
from dotenv import load_dotenv
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import chainlit as cl
from PIL import Image
import google.generativeai as genai
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel(model_name="gemini-2.0-flash")


def save_fig(fig):
    f = tempfile.NamedTemporaryFile(delete=False,suffix=".png")
    fig.savefig(f.name,bbox_inches="tight",dpi=150)
    plt.close(fig)
    return f.name

def df_into_string(df,max_rows=5):
    buf = io.StringIO()
    df.info(buf=buf)
    schema = buf.getvalue()
    head = df.head(max_rows).to_markdown(index=False)

    missing = df.isnull().sum()
    missing  = missing[missing>0]
    missing_info = "No missing values." if missing.empty else str(missing)
    return f"### Schema:\n```\n{schema}```\n\n### Preview:\n{head}\n\n### Missing:\n{missing_info}"

async def ai_text_analysis(prompt_type,df_context):
    prompt = {
        "plan" : f"You are a senior data analyst. Suggest a conscise data analysis plan:\n{df_context}",
        "final": f"Summarize insights from the following dataset:\n{df_context}"
    }
    try:
        res = await model.generate_content_async(
            prompt.get(prompt_type),generation_config=genai.types.GenerationConfig(max_output_tokens=500,temperature=0.3)
        )
        return res.text if res.parts else "Gemini response Blocked."
    except Exception as e:
        return f"Gemini Error : {e}"
    
async def ai_vision_analysis(img_path):
    results = []

    for title,path in img_path:
        try:
            img = Image.open(path)
            res = await model.generate_content_async([f"Explain this '{title}'",img],generation_config=genai.types.GenerationConfig(max_output_tokens=200,temperature=0.2))
            results.append((title,res.text if res.parts else "Blocked or Empty response."))
        except Exception as e:
            results.append((title,f"Error {e}"))
    return results

def generate_visuals(df):
    visualizations = []
    saved_files = []

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = [col for col in df.select_dtypes('object') if 1<df[col].nunique() <30]

    try:
        if len(numeric_cols) >1:
            fig,ax = plt.subplots(figsize=(10,8))
            corr = df[numeric_cols].corr()
            mask = np.triu(np.ones_like(corr,dtype=bool))
            sns.heatmap(corr,mask=mask,cmap="coolwarm",annot=True,fmt=".2f",ax=ax)
            ax.set_title("Correlation Heatmap")
            path = save_fig(fig)
            visualizations.append(("Correlation Heatmap",path))
            saved_files.append(path)

        if len(numeric_cols) >=3:
            sns.set(style="ticks")
            fig = sns.pairplot(df[numeric_cols[:5]].dropna()).fig
            fig.suptitle("Pairplot of Numeric Features",y=1.02)
            path = save_fig(fig)
            visualizations.append(("Pairplot",path))
            saved_files.append(path)

        for col in numeric_cols[:3]:
            fig,ax = plt.subplots(figsize=(8,6))
            sns.violinplot(data=df,y=col,ax=ax)
            ax.set_title(f"Violin Plot for {col}")
            path = save_fig(fig)
            visualizations.append((f"Violin Plot - {col}",path))
            saved_files.append(path)
    
    except Exception as e:
        print(f"Visualisation error : {e}")
        plt.close("all")

    return visualizations,saved_files

async def cleanup(files):
    for f in files:
        try:
            os.remove(f)
        except:
            pass

@cl.on_chat_start
async def start():
    await cl.Message(content="Upload a CSV file for AI Analysis using Gemini").send()
    files = await cl.AskFileMessage(content="Upload a CSV file",accept=["text/csv"]).send()

    if not files:
        return await cl.Message(content="No file received.").send()
    
    processing_msg = cl.Message(content="Processing....")
    await processing_msg.send()

    try:
        file = files[0]
        df = None
        for enc in [None, 'utf-8', 'utf-8-sig', 'cp1252', 'latin1']:
            try:
                if enc is None:
                    df = pd.read_csv(file.path)
                else:
                    df = pd.read_csv(file.path, encoding=enc)
                break
            except UnicodeDecodeError:
                continue
        if df is None:
            with open(file.path, 'r', encoding='utf-8', errors='replace') as f:
                df = pd.read_csv(f)

        if df.empty:
            processing_msg.content = "Empty Dataset."
            await processing_msg.update()
            return
        
        cl.user_session.set("df",df)

        info = df_into_string(df)
        await cl.Message(content=info).send()

        plan = await ai_text_analysis("plan",info)
        await cl.Message(content=f"### AI Plan:\n{plan}").send()

        visualizations, saved_files = generate_visuals(df)
        for title,path in visualizations:
            await cl.Message(content=f"**{title}**",elements=[cl.Image(name=title,path=path)]).send()

        insights = await ai_vision_analysis(visualizations)
        for title,insight in insights:
            await cl.Message(content=f"### {title} Insight\n{insight}").send()

        final = await ai_text_analysis("final",info)
        await cl.Message(content=f"### Final AI Report:\n{final}").send()

        processing_msg.content = "Analysis complete."
        await processing_msg.update()
        await cleanup(saved_files)

    except Exception as e:
        traceback.print_exc()
        processing_msg.content = f"Error: {e}"
        await processing_msg.update()