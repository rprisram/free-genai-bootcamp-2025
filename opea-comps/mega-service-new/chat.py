from comps import ServiceOrchestrator,MicroService,ServiceRoleType,ServiceType
from comps.cores.proto.api_protocol import ChatCompletionRequest, ChatCompletionResponse, ChatMessage, UsageInfo, ChatCompletionResponseChoice
from fastapi import HTTPException
from fastapi import requests
class Chat:
    def __init__(self, host="0.0.0.0", port=8000): 
        self.host = host
        self.port = port
        self.megaservice = ServiceOrchestrator()
        self.endpoint = "/v1/chat-service"
        print('hello')
    
    def start(self):
        self.service = MicroService(
            self.__class__.__name__,
            service_role=ServiceRoleType.MEGASERVICE,
            host=self.host,
            port=self.port,
            endpoint=self.endpoint,
            input_datatype=ChatCompletionRequest,
            output_datatype=ChatCompletionResponse,
        )
        self.service.add_route(self.endpoint, self.handle_request, methods=["POST"])
        self.service.start()

    def add_remote_service(self):
        print('add_remote_services')
        #embedding = MicroService(
        #   name="embedding",
        #   host=EMBEDDING_SERVICE_HOST_IP,
        #   port=EMBEDDING_SERVICE_PORT,
        #   endpoint="/v1/embeddings",
        #   use_remote_service=True,
        #   service_type=ServiceType.EMBEDDING,
        #)
      # llm = MicroService(
      #     name="llm",
      #     host=LLM_SERVICE_HOST_IP,
      #     port=LLM_SERVICE_PORT,
      #     endpoint="/v1/chat/completions",
      #     use_remote_service=True,
      #     service_type=ServiceType.LLM,
      # )
        #self.megaservice.add(embedding).add(llm)
        #self.megaservice.flow_to(embedding, llm)
       # self.megaservice.add(llm)
        #self.megaservice.flow_to(llm)
    
    async def handle_request(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
            try:
                # Format the request for Ollama
                ollama_request = {
                    "model": request.model or "llama3.2:1b",  # or whatever default model you're using
                    "messages": [
                        {
                            "role": "user",
                            "content": request.messages  # assuming messages is a string
                        }
                    ],
                    "stream": False  # disable streaming for now
                }
                
                # Schedule the request through the orchestrator
                result = await self.megaservice.schedule(ollama_request)
                
                # Extract the actual content from the response
                if isinstance(result, tuple) and len(result) > 0:
                    llm_response = result[0].get('llm/MicroService')
                    if hasattr(llm_response, 'body'):
                        # Read and process the response
                        response_body = b""
                        async for chunk in llm_response.body_iterator:
                            response_body += chunk
                        content = response_body.decode('utf-8')
                    else:
                        content = "No response content available"
                else:
                    content = "Invalid response format"

                # Create the response
                response = ChatCompletionResponse(
                    model=request.model or "example-model",
                    choices=[
                        ChatCompletionResponseChoice(
                            index=0,
                            message=ChatMessage(
                                role="assistant",
                                content=content
                            ),
                            finish_reason="stop"
                        )
                    ],
                    usage=UsageInfo(
                        prompt_tokens=0,
                        completion_tokens=0,
                        total_tokens=0
                    )
                )
                
                return response
                
            except Exception as e:
                # Handle any errors
                raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    chat = Chat()
    chat.add_remote_service()
    try:
        chat.start()
    except requests.exceptions.ConnectionError as e:
        if "localhost:4318" in str(e) and "Connection refused" in str(e):
            print("Warning: OpenTelemetry connection failed. Continuing without telemetry.")
        else:
            # Re-raise if it's a different connection error
            raise  