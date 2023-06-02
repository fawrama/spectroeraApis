from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import connect_AWS
import connect_supabase
app = FastAPI()

# Define a Pydantic model for the input parameters


class InputParams(BaseModel):
    userId: str
    

# Use the model as a query parameter for the endpoint


@app.get("/")
async def getPredictions(params: InputParams):
    # Validate the input parameters and raise exceptions if any are missing or invalid
    if params.userId == '':
        raise HTTPException(status_code=404, detail="userID is not provided")
    userDetails = connect_supabase.getUserDetails(params.userId)

    # Call the connect_AWS functions to get the predictions
    predictedHeartDisease = int(connect_AWS.predict_heart_disease(params.userId))
    if predictedHeartDisease > 0:
        heartDisease = 1
        if predictedHeartDisease == 1:
            disease = 'supra-ventricular premature'
        elif predictedHeartDisease ==2:
            disease = 'ventricular escape'
        elif predictedHeartDisease == 3:
            disease = 'fusion of ventricular'
        else:
            disease = 'Unknown'
    else:
        heartDisease = 0
        disease = 'normal'

    predictedStrokeProba = connect_AWS.predict_stroke(
        connect_AWS.stroke_models,
        userDetails['gender'],
        userDetails['age'],
        userDetails['hypertension'],
        heartDisease,
        userDetails['marriage_status'],
        userDetails['work_type'],
        userDetails['residence_type'],
        userDetails['avg_glucose'],
        userDetails['bmi'],
        userDetails['smoking_status'])

    # Determine if medical attention is needed based on the stroke probability
    if int(predictedStrokeProba) > 20:
        medicalAttention = 'YES'
    else:
        medicalAttention = 'NO'
    # Create a JSON object for the response with the predictions and the medical attention flag
    response = {
        "predictedStrokeProba": '{:.2f}'.format(predictedStrokeProba),
        "predictedHeartDisease": disease,
        'medicalAttentionNeeded': medicalAttention
    }
    connect_supabase.saveUserResults(params.userId,response)
    # Return the response as a JSON object
    return response