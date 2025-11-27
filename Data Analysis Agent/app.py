import os,io,tempfile,traceback,asyncio
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
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, DeadlineExceeded

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel(model_name="gemini-2.0-flash")

async def _gemini_call_with_backoff(parts, max_tokens=750, temperature=0.3, max_retries=5, initial_delay=1.0):
    delay = initial_delay
    last_err = None
    for attempt in range(max_retries):
        try:
            res = await model.generate_content_async(
                parts,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )
            return res
        except (ResourceExhausted, ServiceUnavailable, DeadlineExceeded) as e:
            last_err = e
        except Exception as e:
            msg = str(e).lower()
            if any(k in msg for k in ["rate", "quota", "429", "resource exhausted", "exceeded"]):
                last_err = e
            else:
                raise
        await asyncio.sleep(delay)
        delay = min(delay * 2, 8.0)
    raise last_err if last_err else RuntimeError("Gemini call failed without explicit error")

def save_fig(fig):
    f = tempfile.NamedTemporaryFile(delete=False,suffix=".png")
    fig.savefig(f.name,bbox_inches="tight",dpi=150)
    plt.close(fig)
    return f.name

def save_text(text: str, suffix: str = ".md"):
    f = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    with open(f.name, "w", encoding="utf-8") as out:
        out.write(text)
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
        "plan" : f"You are a senior data analyst. Suggest a concise data analysis plan:\n{df_context}",
        "final": f"Summarize insights from the following dataset:\n{df_context}"
    }
    try:
        await asyncio.sleep(0.8)
        res = await _gemini_call_with_backoff(
            prompt.get(prompt_type),
            max_tokens=750,
            temperature=0.3,
        )
        return res.text if res.parts else "Gemini response Blocked."

    except Exception as e:
        return f"Gemini Error : {e}"
    
async def ai_vision_analysis(img_path):

    results = []

    for title,path in img_path:
        try:
            img = Image.open(path)
            await asyncio.sleep(0.8)
            res = await _gemini_call_with_backoff(
                [f"Explain this '{title}'", img],
                max_tokens=300,
                temperature=0.2,
            )
            results.append((title, res.text if res.parts else "Blocked or Empty response."))

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

        for col in numeric_cols[:5]:
            fig, ax = plt.subplots(figsize=(8,6))
            sns.histplot(df[col].dropna(), kde=True, ax=ax)
            ax.set_title(f"Histogram - {col}")
            path = save_fig(fig)
            visualizations.append((f"Histogram - {col}", path))
            saved_files.append(path)

        for col in numeric_cols[:5]:
            fig, ax = plt.subplots(figsize=(8,6))
            sns.boxplot(y=df[col], ax=ax)
            ax.set_title(f"Box Plot - {col}")
            path = save_fig(fig)
            visualizations.append((f"Box Plot - {col}", path))
            saved_files.append(path)

        for col in categorical_cols[:5]:
            fig, ax = plt.subplots(figsize=(10,6))
            order = df[col].value_counts().index[:10]
            sns.countplot(x=col, data=df, order=order, ax=ax)
            ax.set_title(f"Countplot - {col}")
            ax.tick_params(axis='x', rotation=45)
            path = save_fig(fig)
            visualizations.append((f"Countplot - {col}", path))
            saved_files.append(path)

        churn_candidates = [c for c in df.columns if 'churn' in str(c).lower()]
        if churn_candidates:
            churn_col = churn_candidates[0]
            target = df[churn_col]
            target_num = None
            if pd.api.types.is_numeric_dtype(target):
                target_num = target
            else:
                target_num = pd.to_numeric(target, errors='coerce')
                if target_num.isna().all():
                    mapping = {
                        'yes': 1, 'no': 0,
                        'y': 1, 'n': 0,
                        'true': 1, 'false': 0,
                        't': 1, 'f': 0,
                        '1': 1, '0': 0
                    }
                    target_num = target.astype(str).str.strip().str.lower().map(mapping)
            tmp_df = df[numeric_cols].copy()
            tmp_df['__churn__'] = target_num
            corrs = tmp_df.corr(numeric_only=True)['__churn__'].dropna()
            corrs = corrs.drop(labels='__churn__', errors='ignore')
            if not corrs.empty:
                top_corr = corrs.reindex(corrs.abs().sort_values(ascending=False).index)[:10]
                fig, ax = plt.subplots(figsize=(10,6))
                sns.barplot(x=top_corr.values, y=top_corr.index, ax=ax, orient='h')
                ax.set_title(f"Top Correlated with {churn_col}")
                ax.set_xlabel("Correlation")
                ax.set_ylabel("Feature")
                path = save_fig(fig)
                visualizations.append((f"Top Correlated with {churn_col}", path))
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

def _chunk_text(text: str, size: int = 120):
    for i in range(0, len(text), size):
        yield text[i:i+size]

async def stream_markdown(title: str, body: str):
    msg = cl.Message(content=f"### {title}\n")
    await msg.send()
    for chunk in _chunk_text(body):
        await msg.stream_token(chunk)
        await asyncio.sleep(0.02)
    await msg.update()

@cl.step(name="Dataset Summary")
async def step_dataset_summary(info_md: str):
    await stream_markdown("Dataset Summary", info_md)

@cl.step(name="AI Plan")
async def step_ai_plan(plan_md: str):
    await stream_markdown("AI Plan", plan_md)

@cl.step(name="Visualizations")
async def step_visualizations(visualizations):
    vis_elements = [cl.Image(name=title, path=path, display="side") for title, path in visualizations]
    vis_list_md = "\n".join([f"- {title}" for title, _ in visualizations]) or "- No visuals generated"
    msg = cl.Message(content="## Visualizations\nOpen images from the sidebar.\n\n", elements=vis_elements)
    await msg.send()
    for chunk in _chunk_text(vis_list_md):
        await msg.stream_token(chunk)
        await asyncio.sleep(0.02)
    await msg.update()

@cl.step(name="Visual Insights")
async def step_visual_insights_streaming(visualizations):
    msg = cl.Message(content="### Visual Insights\n")
    await msg.send()
    if not visualizations:
        await msg.stream_token("No insights.")
        await msg.update()
        return
    for title, path in visualizations:
        try:
            header = f"\n\n#### {title}\n"
            for chunk in _chunk_text(header):
                await msg.stream_token(chunk)
                await asyncio.sleep(0.01)
            img = Image.open(path)
            await asyncio.sleep(0.8)
            res = await _gemini_call_with_backoff([f"Explain this '{title}'", img], max_tokens=300, temperature=0.2)
            text = res.text if res.parts else "Blocked or Empty response."
            for chunk in _chunk_text(text):
                await msg.stream_token(chunk)
                await asyncio.sleep(0.02)
        except Exception as e:
            err = f"\n\n#### {title}\nError: {e}"
            for chunk in _chunk_text(err):
                await msg.stream_token(chunk)
                await asyncio.sleep(0.01)
    await msg.update()

@cl.step(name="Final AI Report")
async def step_final_report(final_md: str):
    await stream_markdown("Final AI Report", final_md)

@cl.on_chat_start
async def start():
    await cl.Message(content="Upload a CSV file for AI Analysis using Gemini").send()
    files = await cl.AskFileMessage(content="Upload a CSV file",accept=["text/csv"]).send()

    if not files:
        return await cl.Message(content="No file received.").send()
    
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
            await cl.Message(content="Empty Dataset.").send()
            return
        
        cl.user_session.set("df",df)

        info = df_into_string(df)
        await step_dataset_summary(info)

        plan = await ai_text_analysis("plan",info)
        await step_ai_plan(plan)

        visualizations, saved_files = generate_visuals(df)
        await step_visualizations(visualizations)

        await step_visual_insights_streaming(visualizations)

        await asyncio.sleep(0.8)
        final = await ai_text_analysis("final",info)
        await step_final_report(final)

        await cl.Message(content="Analysis complete.").send()
        await cleanup(saved_files)

    except Exception as e:
        traceback.print_exc()
        await cl.Message(content=f"Error: {e}").send()