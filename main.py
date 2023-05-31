from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import connect_AWS
import json

app = FastAPI()

# Define a Pydantic model for the input parameters
class InputParams(BaseModel):
    userId: str
    gender: str
    age: int
    hyperTension: int # Change this to int
    everMarried: str
    workType: str
    residenceType: str
    AGL: float
    BMI: float
    smokingStatus: str

# Use the model as a query parameter for the endpoint
@app.get("/")
async def getPredictions(params: InputParams):
    # Validate the input parameters and raise exceptions if any are missing or invalid
    if params.userId == '':
        raise HTTPException(status_code=404, detail="userID is not provided")
    elif params.gender not in ['Male', 'Female', 'Other']:
        raise HTTPException(status_code=404, detail="Gender is not valid")
    elif params.age <= 0:
        raise HTTPException(status_code=404, detail="Age is not positive")
    elif params.hyperTension not in [0, 1]: # Change this to [0, 1]
        raise HTTPException(
            status_code=404, detail="hyper tension is not valid")
    elif params.everMarried not in ['Yes', 'No']:
        raise HTTPException(
            status_code=404, detail="marriage status is not valid")
    elif params.workType not in ['Private', 'Self-employed', 'Govt_job', 'children', 'Never_worked']:
        raise HTTPException(
            status_code=404, detail="Work type is not valid")
    elif params.residenceType not in ['Urban', 'Rural']:
        raise HTTPException(
            status_code=404, detail="Residence type is not valid")
    elif params.AGL <= 0:
        raise HTTPException(
            status_code=404, detail="average glucose level is not positive")
    elif params.BMI <= 0:
        raise HTTPException(status_code=404, detail="BMI is not positive")
    elif params.smokingStatus not in ['formerly smoked', 'never smoked', 'smokes', 'Unknown']:
        raise HTTPException(
            status_code=404, detail="Smoking status type is not valid")

    # Call the connect_AWS functions to get the predictions
    predictedHeartDisease = connect_AWS.predict_heart_disease(params.userId)
    print(predictedHeartDisease)
    predictedStrokeProba = connect_AWS.predict_stroke(
        connect_AWS.stroke_models,
        params.gender,
        params.age,
        params.hyperTension,
        predictedHeartDisease,
        params.everMarried,
        params.workType,
        params.residenceType,
        params.AGL,
        params.BMI,
        params.smokingStatus)

    # Determine if medical attention is needed based on the stroke probability
    if int(predictedStrokeProba) > 20:
        medicalAttention = 'YES'
    else:
        medicalAttention = 'NO'

    # Create a JSON object for the response with the predictions and the medical attention flag
    response = {
        "predictedStrokeProba": '{:.2f}'.format(predictedStrokeProba),
        "predictedHeartDisease": str(predictedHeartDisease),
        'medicalAttentionNeeded': medicalAttention
    }
    
    # Return the response as a JSON object
    return response
