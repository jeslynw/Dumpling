# Input type strings — stored on SQLite File.input_type for record-keeping
# No longer used for routing (router.py removed).
# agent_ingestion decides which tool to use by inspecting content itself.
# pipeline.py store_node uses _detect_input_type() for storage labelling only.
INPUT_TYPE_TEXT = "text"
INPUT_TYPE_LINK = "link"
INPUT_TYPE_IMAGE = "image"
INPUT_TYPE_DOCUMENT = "document"    # PDF or DOCX