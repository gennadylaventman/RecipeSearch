docker run -d \
  --name qdrant_container \
  --network my_bridge \
  -p 6333:6333 \
  -v /home/gena/IdeaProjects/PyProj/TextProcessing/qdrant_data:/qdrant/storage \
  -e QDRANT__STORAGE__MEMORY="4GB" \
  -e QDRANT__SERVICE__MAX_THREADS=4 \
  qdrant/qdrant

