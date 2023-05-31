from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, validator
import connect_AWS
import json

app = FastAPI()

# Define a Pydantic model for the input parameters
class InputParams(BaseModel):
    userId: str
    gender: str
    age: int
    hyperTension: int 
    everMarried: str
    workType: str
    residenceType: str
    AGL: float
    BMI: float
    smokingStatus: str

    # Use Pydantic validators to check the values of the input parameters and raise custom errors if they are invalid
    @validator('userId')
    def user_id_must_not_be_empty(cls, v):
        if v == '':
            raise ValueError('userID is not provided')
        return v
    
    @validator('gender')
    def gender_must_be_valid(cls, v):
        if v not in ['Male', 'Female', 'Other']:
            raise ValueError('Gender is not valid')
        return v
    
    @validator('age')
    def age_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Age is not positive')
        return v
    
    @validator('hyperTension')
    def hyper_tension_must_be_valid(cls, v):
        if v not in [0, 1]:
            raise ValueError('hyper tension is not valid')
        return v
    
    @validator('everMarried')
    def marriage_status_must_be_valid(cls, v):
        if v not in ['Yes', 'No']:
            raise ValueError('marriage status is not valid')
        return v
    
    @validator('workType')
    def work_type_must_be_valid(cls, v):
        if v not in ['Private', 'Self-employed', 'Govt_job', 'children', 'Never_worked']:
            raise ValueError('Work type is not valid')
        return v
    
    @validator('residenceType')
    def residence_type_must_be_valid(cls, v):
        if v not in ['Urban', 'Rural']:
            raise ValueError('Residence type is not valid')
        return v
    
    @validator('AGL')
    def agl_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('average glucose level is not positive')
        return v
    
    @validator('BMI')
    def bmi_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('BMI is not positive')
        return v
    
    @validator('smokingStatus')
    def smoking_status_must_be_valid(cls, v):
        if v not in ['formerly smoked', 'never smoked', 'smokes', 'Unknown']:
            raise ValueError('Smoking status type is not valid')
        return v

# Define a FastAPI dependency to inject the input parameters into the endpoint function
def get_params(params: InputParams = Depends()):
    return params

# Use the dependency as a query parameter for the endpoint
@app.get("/")
async def getPredictions(params: InputParams = Depends(get_params)):
    
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
    # Use f-strings to format the values instead of .format()
    response = {
        "predictedStrokeProba": f"{predictedStrokeProba:.2f}",
        "predictedHeartDisease": str(predictedHeartDisease),
        'medicalAttentionNeeded': medicalAttention
    }
    
    # Return the response as a JSON object
    return response
