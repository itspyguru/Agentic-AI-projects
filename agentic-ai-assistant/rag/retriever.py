def retrieve_documents(vector_store, query, top_k=5):
    # Retrieve relevant documents from the vector store based on the query
    retriever = vector_store.as_retriever(search_kwargs={"k": top_k})                         
    return retriever.invoke(query)
