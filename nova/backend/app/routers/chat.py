from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.misc import Conversation, Message, MemoryEntry
from app.models.user import User
from app.schemas.chat import ChatMessageIn, ChatReplyOut, ConversationOut, MemoryEntryOut, MessageOut
from app.services import ai, memory

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatReplyOut)
def send_message(payload: ChatMessageIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == payload.conversation_id, Conversation.user_id == user.id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(user_id=user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    user_message = Message(conversation_id=conversation.id, sender="user", text_content=payload.text)
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    context = memory.get_short_term_context(db, conversation.id)
    result = ai.generate_reply(payload.text, context_messages=context)

    assistant_message = Message(conversation_id=conversation.id, sender="assistant", text_content=result["reply"])
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    memory.update_long_term_memory(db, user.id, payload.text)
    memory.maybe_summarize(db, conversation)

    return ChatReplyOut(
        conversation_id=conversation.id,
        user_message=user_message,
        assistant_message=assistant_message,
        source=result["source"],
    )


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Conversation).filter(Conversation.user_id == user.id).order_by(Conversation.created_at.desc()).all()


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageOut])
def get_messages(conversation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id, Conversation.user_id == user.id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()


@router.get("/memory", response_model=list[MemoryEntryOut])
def list_memory(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(MemoryEntry).filter(MemoryEntry.user_id == user.id).all()
