import io
import os
from logicRAG.fileProcessor import Processor


options = ["Mail Database"]


temp_paths = r"C:\Users\admin\chatbot_demo\crawl_data"
for path_name in os.listdir(temp_paths):
    #print(os.path.join(temp_paths, path_name))
    with open(os.path.join(temp_paths, path_name), "rb") as f:
        file = f.read()
    file_obj = io.BytesIO(file)
    file_obj.name = "sample.pdf"


    processor = Processor(file_obj, options, 200)
    text, chunks, embeddings = processor.process()
    print(text)

#10/7: chưa xong, đang dở dang
