import os
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite",google_api_key=api_key)

qa_chain = None
current_video_id = None


def extract_video_id(url: str) -> str:
    parsed = urlparse(url)

    if parsed.hostname in ("youtu.be", "www.youtu.be"):
        video_id = parsed.path.strip("/").split("/")[0]

    elif parsed.hostname in (
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
    ):
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        elif parsed.path.startswith(("/embed/", "/shorts/")):
            video_id = parsed.path.split("/")[2]
        else:
            video_id = None
    else:
        video_id = None

    if not video_id:
        raise ValueError("Invalid YouTube video URL")

    return video_id


def process_video(url: str) -> str:
    global qa_chain, current_video_id

    video_id = extract_video_id(url)

    transcript_list = YouTubeTranscriptApi().fetch(video_id, languages=["en"])

    transcript = " ".join(snippet.text for snippet in transcript_list)

    splitter = RecursiveCharacterTextSplitter(chunk_size=2000,chunk_overlap=200)
    
    chunks = splitter.create_documents([transcript])
    vector_db = FAISS.from_documents(chunks, embeddings)

    retriever = vector_db.as_retriever(search_type="similarity",search_kwargs={"k": 4})

    prompt = PromptTemplate(
        template="""
        You are a helpful assistant.
        Answer ONLY using the provided video transcript context.
        If the context is insufficient, say you don't know.

        Transcript context:
        {context}

        Question: {question}
        """,
        input_variables=["context", "question"],
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    parallel_chain = RunnableParallel({
        "context": retriever | RunnableLambda(format_docs),
        "question": RunnablePassthrough(),
    })

    qa_chain = parallel_chain | prompt | llm | StrOutputParser()
    current_video_id = video_id

    return video_id


def ask_question(question: str) -> str:
    if qa_chain is None:
        raise ValueError("Please process a YouTube video first")

    return qa_chain.invoke(question)
