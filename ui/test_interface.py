"""
🧪 AI Voice Agent Testing Interface
Interactive web UI to test the pipeline without phone calls
"""

import streamlit as st
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from app.rag.local_embeddings import LocalEmbedder, TRANSFORMERS_AVAILABLE
from app.rag.vector_store import VectorStore
from app.llm.local_responder import generate_response_local, test_local_llm
from app.config.loader import load_org_config

# Page config
st.set_page_config(
    page_title="AI Voice Agent Test Lab",
    page_icon="🧪",
    layout="wide"
)

# Title
st.title("🧪 AI Voice Agent - Test Lab")
st.markdown("**Test queries without phone calls • See RAG in action • Debug pipeline**")
st.divider()

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Organization selection
    org_name = st.selectbox(
        "Organization",
        ["sample_org"],
        help="Select organization to test"
    )
    
    # Model selection
    use_local = st.radio(
        "AI Model",
        ["FREE (Local)", "OpenAI (Requires API Key)"],
        index=0,
        help="Choose between local models (free) or OpenAI (paid)"
    )
    
    st.divider()
    
    # System status
    st.subheader("🔧 System Status")
    
    # Check Ollama
    ollama_working, ollama_models = test_local_llm()
    if ollama_working:
        st.success("✅ Ollama Running")
        st.caption(f"Models: {', '.join(ollama_models[:2])}")
    else:
        st.error("❌ Ollama Not Running")
        st.caption("Run: `ollama serve`")
    
    # Check embeddings
    if TRANSFORMERS_AVAILABLE:
        st.success("✅ sentence-transformers")
    else:
        st.error("❌ sentence-transformers")
    
    # Check vector store
    vector_store_path = f"data/{org_name}/vector_store_local"
    if Path(vector_store_path).exists():
        st.success("✅ Vector Store Loaded")
    else:
        st.error("❌ Vector Store Missing")
        st.caption("Run ingestion script")
    
    st.divider()
    
    # Advanced settings
    with st.expander("🔬 Advanced Settings"):
        num_results = st.slider("RAG Results (k)", 1, 5, 3)
        temperature = st.slider("LLM Temperature", 0.0, 1.0, 0.7)
        show_debug = st.checkbox("Show Debug Info", value=True)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("💬 Test Query")
    
    # Quick examples
    st.caption("Quick examples:")
    example_queries = {
        "Operating Hours": "What are your operating hours?",
        "Contact Info": "How can I contact support?",
        "Services": "What services do you offer?",
        "Admissions": "What are the admission requirements?",
        "Custom": ""
    }
    
    example = st.selectbox("Select example or write custom:", list(example_queries.keys()))
    
    if example == "Custom":
        user_query = st.text_area(
            "Your question:",
            height=100,
            placeholder="Type your question here..."
        )
    else:
        user_query = st.text_area(
            "Your question:",
            value=example_queries[example],
            height=100
        )
    
    test_button = st.button("🚀 Test Query", type="primary", use_container_width=True)

with col2:
    st.subheader("🎯 AI Response")
    response_placeholder = st.empty()

# Process query
if test_button and user_query:
    with st.spinner("Processing..."):
        start_time = time.time()
        
        # Load config
        try:
            config = load_org_config(org_name)
            st.success(f"✓ Loaded config for: {config['org_name']}")
        except Exception as e:
            st.error(f"Failed to load config: {e}")
            st.stop()
        
        # Load vector store
        try:
            vector_store = VectorStore(dimension=384)
            vector_store.load(vector_store_path)
            st.success(f"✓ Loaded vector store ({len(vector_store.chunks)} documents)")
        except Exception as e:
            st.error(f"Failed to load vector store: {e}")
            st.stop()
        
        # Create embeddings and search
        try:
            embedder = LocalEmbedder("all-MiniLM-L6-v2")
            
            with st.status("🔍 Searching knowledge base..."):
                st.write("Creating query embedding...")
                query_embedding = embedder.embed_text(user_query)
                
                st.write("Searching for relevant documents...")
                results = vector_store.search(query_embedding, k=num_results)
                
                st.write(f"Found {len(results)} relevant documents")
            
            # Extract context
            context_chunks = [chunk for chunk, _, _ in results]
            
        except Exception as e:
            st.error(f"Search failed: {e}")
            st.stop()
        
        # Generate response
        try:
            with st.status("🤖 Generating AI response..."):
                if use_local == "FREE (Local)":
                    response = generate_response_local(
                        user_query,
                        context_chunks,
                        model="llama3.2:3b"
                    )
                else:
                    st.warning("OpenAI integration not configured in UI yet")
                    response = "OpenAI mode not implemented yet. Use FREE mode."
            
            end_time = time.time()
            
        except Exception as e:
            st.error(f"Response generation failed: {e}")
            response = "Error generating response"
            end_time = time.time()
        
        # Display response
        with col2:
            st.markdown("### 💬 Response")
            st.info(response)
            st.caption(f"⏱️ Generated in {end_time - start_time:.2f}s")
        
        # Show RAG retrieval details
        st.divider()
        st.subheader("📚 RAG Retrieval Results")
        
        for i, (chunk, metadata, distance) in enumerate(results, 1):
            with st.expander(f"📄 Result {i} - Distance: {distance:.2f}"):
                st.markdown(f"**Source:** {metadata.get('filename', 'Unknown')}")
                st.markdown(f"**Similarity Score:** {1 / (1 + distance):.2%}")
                st.text_area(
                    f"Content",
                    value=chunk,
                    height=150,
                    key=f"chunk_{i}",
                    disabled=True
                )
        
        # Debug info
        if show_debug:
            st.divider()
            st.subheader("🔬 Debug Information")
            
            debug_col1, debug_col2, debug_col3 = st.columns(3)
            
            with debug_col1:
                st.metric("Processing Time", f"{end_time - start_time:.2f}s")
            
            with debug_col2:
                st.metric("Documents Retrieved", len(results))
            
            with debug_col3:
                st.metric("Embedding Dimension", len(query_embedding))
            
            with st.expander("📊 Detailed Metrics"):
                st.json({
                    "query": user_query,
                    "query_length": len(user_query),
                    "embedding_dimension": len(query_embedding),
                    "num_chunks_in_store": len(vector_store.chunks),
                    "num_results_returned": len(results),
                    "model_used": "llama3.2:3b" if use_local == "FREE (Local)" else "OpenAI",
                    "processing_time_seconds": round(end_time - start_time, 3),
                    "context_length": sum(len(c) for c in context_chunks),
                })

elif test_button and not user_query:
    st.warning("⚠️ Please enter a question")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("💰 **Cost:** $0.00 (Using local models)")

with col2:
    st.caption("🚀 **Status:** Ready to test")

with col3:
    st.caption("🔧 **Mode:** Development")

# Instructions
with st.expander("ℹ️ How to Use"):
    st.markdown("""
    ### Quick Start
    1. **Select an example query** or write your own
    2. **Click "Test Query"** to see the magic happen
    3. **View AI response** and see which documents were used
    4. **Check debug info** to understand the pipeline
    
    ### What This Tests
    - ✅ Document retrieval (RAG)
    - ✅ Semantic similarity search
    - ✅ LLM response generation
    - ✅ Complete pipeline timing
    
    ### Troubleshooting
    - **Ollama not running?** Run: `ollama serve` in terminal
    - **Vector store missing?** Run: `python scripts/ingest_documents_free.py --org sample_org`
    - **Slow responses?** Use smaller Ollama model: `ollama pull llama3.2:1b`
    
    ### Cost
    This interface uses **100% FREE local models**:
    - Ollama (LLM): $0.00
    - sentence-transformers (Embeddings): $0.00
    - FAISS (Vector Store): $0.00
    """)

# Note about phone calls
st.info("💡 **Note:** This interface simulates the voice agent pipeline. In production, users would interact via phone calls, but this lets you test everything visually!")
