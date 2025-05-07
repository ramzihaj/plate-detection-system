   from fastapi import FastAPI, File, UploadFile
   from fastapi.responses import JSONResponse
   from fastapi.middleware.cors import CORSMiddleware
   import base64

   app = FastAPI()

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:4200"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )

   @app.post("/detect")
   async def detect_plate(file: UploadFile = File(...)):
       # Simuler une détection (remplace par ton modèle YOLOv8)
       content = await file.read()
       # Simuler un texte de plaque
       plate_text = "123 TUN 456"
       # Simuler une image annotée (retourne le même fichier en base64)
       img_base64 = base64.b64encode(content).decode('utf-8')

       return JSONResponse({
           "plateText": plate_text,
           "image": f"data:image/jpeg;base64,{img_base64}"
       })