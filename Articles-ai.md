[Building an AI Blog Generator with FastAPI, React, and Hugging Face](https://dev.to/lymah/building-an-ai-blog-generator-with-fastapi-react-and-hugging-face-49m5)

[Demystifying Semantic Drift in Embeddings](https://www.c-sharpcorner.com/article/demystifying-semantic-drift-in-embeddings)

Running the POC
- Start the backend: uvicorn main:app --reload

- Start the frontend: streamlit run app.py

- Test Case: Ask "What are the hedging requirements for interest rates?". The Drift Detector will flag the initial mock LIBOR retrieval as drifted, trigger the re_retrieve node, and generate an answer based on SOFR.
