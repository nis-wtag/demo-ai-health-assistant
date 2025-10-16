from fastapi import APIRouter, Cookie, Depends, HTTPException, Request
from models.user import User
from schemas.chat_schema import ChatQuery, ChatResponse
from services.dependencies.auth_dependencies import get_current_user, require_roles
from services.llm_query_service import QueryService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def process_chat_query(
    chat_in: ChatQuery,
    current_user: User = Depends(get_current_user),
    query_service: QueryService = Depends(),
):
    output = {
        "disclaimer": "This is AI-generated advice and not a substitute for professional medical consultation. Please see a certified doctor for any health concerns.",
        "remedy": "For a common cold and headache, ensure you get adequate rest and stay hydrated by drinking plenty of warm fluids like water, soup, or tea. Gargling with warm salt water can help soothe a sore throat. Over-the-counter pain relievers such as paracetamol may also help manage the headache.",
        "recommended_doctors": [
            {
                "id": 101,
                "full_name": "Dr. Afroza Suraya Majumder",
                "degrees": ["MBBS", "DLO (ENT)"],
                "specialization": "ENT Specialist & Head Neck Surgeon",
                "designation": "Assistant Professor, ENT",
                "affiliated_hospital": "Anwer Khan Modern Medical College & Hospital",
                "chambers": [
                    {
                        "id": 201,
                        "contact_number": "+8801757138425",
                        "chamber_id": 301,
                        "chamber_name": "Anwer Khan Modern Medical College Hospital",
                        "address": "House # 17, Road # 08, Dhanmondi R/A, Dhaka – 1205",
                        "longitude": 90.382072,
                        "latitude": 23.743232,
                        "visiting_hours": [
                            {
                                "id": 401,
                                "day": "Monday",
                                "start_time": "19:00:00",
                                "end_time": "21:00:00",
                            },
                            {
                                "id": 402,
                                "day": "Wednesday",
                                "start_time": "19:00:00",
                                "end_time": "21:00:00",
                            },
                        ],
                    }
                ],
            },
            {
                "id": 102,
                "full_name": "Dr. Md. Moniruzzaman",
                "degrees": ["MBBS", "FCPS (Medicine)"],
                "specialization": "Medicine Specialist",
                "designation": "Associate Professor, Medicine",
                "affiliated_hospital": "Dhaka Medical College & Hospital",
                "chambers": [
                    {
                        "id": 202,
                        "contact_number": "+8801911123456",
                        "chamber_id": 302,
                        "chamber_name": "Popular Diagnostic Center, Dhanmondi",
                        "address": "House #16, Road # 2, Dhanmondi, Dhaka 1205",
                        "longitude": 90.37,
                        "latitude": 23.74,
                        "visiting_hours": [
                            {
                                "id": 403,
                                "day": "Saturday",
                                "start_time": "18:00:00",
                                "end_time": "22:00:00",
                            },
                            {
                                "id": 404,
                                "day": "Tuesday",
                                "start_time": "18:00:00",
                                "end_time": "22:00:00",
                            },
                            {
                                "id": 405,
                                "day": "Thursday",
                                "start_time": "18:00:00",
                                "end_time": "22:00:00",
                            },
                        ],
                    }
                ],
            },
        ],
    }

    return ChatResponse(**output)

    # return query_service.process_user_query(user_query=chat_in.query)
