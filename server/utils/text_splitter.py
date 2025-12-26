from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_text(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    return splitter.split_text(docs)
