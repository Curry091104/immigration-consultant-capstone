from app import app
from views.faq_saving import router as faq_saving_router
from views.pdf_saving import router as pdf_saving_router

app.include_router(faq_saving_router)
app.include_router(pdf_saving_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)