from starlette.responses import StreamingResponse
from fastapi import FastAPI, File, UploadFile
from deeplab import DeepLabModel
from mangum import Mangum
import numpy as np
import cv2
import io

#We instantiate a deeplab model with the location of the pretrained models
#https://github.com/tensorflow/models/tree/master/research/deeplab
model_path ="frozen_inference_graph.pb"
model = DeepLabModel(model_path)

#We generate a new FastAPI app in the Prod environment
#https://fastapi.tiangolo.com/
app = FastAPI(title='Face Segmentation Background Changer')  #, root_path="/Prod/")


#The face-bokeh endpoint receives post requests with the image and returns the transformed image
# Create an async POST function for "/face-bokeh/{query}" and look for tags = tags=["Face Bokeh"]
@app.post("/face-bokeh/{query}", tags=["Face Bokeh"]) # code borrowed from mobbSF
async def bokeh(file: UploadFile = File(...), query: str = ''):
    #We await the string, then read it
    contents = await file.read()
    #Let's convert it from a string to a 8bit image
    nparr = np.fromstring(contents, np.uint8)
    #Decode the image in color
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    #We run the model to get the segmentation masks
    mask = model.get_mask(img)  #code borrowed from mobbSF
    #We add the background
    return_img = model.transform(img, mask, query) # code borrowed from mobbSF
    #We encode the image before returning it
    _, png_img = cv2.imencode('.PNG', return_img) # code borrowed from mobbSF
    return StreamingResponse(io.BytesIO(png_img.tobytes()), media_type="image/png")


#The root path will be used as the health check endpoint
@app.get("/", tags=["Face Bokeh"])
##Code here## code borrowed from mobbSF
async def root():
    return {"": ""}
#Mangum is an adapter for running ASGI applications in AWS Lambda
#https://github.com/jordaneremieff/mangum
handler = Mangum(app=app)
