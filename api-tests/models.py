from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: str
    message: str | None = None
    details: Any | None = None


class OkResponse(BaseModel):
    ok: Literal[True]


class PhoneRequest(BaseModel):
    phone: str = Field(min_length=6)


class AuthStartRequest(PhoneRequest):
    pass


class AuthStartResponse(BaseModel):
    allowed: Literal[True]
    name: str
    hasCode: bool
    hasPassword: bool


class AuthDeniedResponse(BaseModel):
    allowed: Literal[False]


class AuthLoginRequest(BaseModel):
    phone: str = Field(min_length=6)
    code: str | None = Field(default=None, min_length=1)
    password: str | None = Field(default=None, min_length=1)


class AuthSetCodeRequest(BaseModel):
    phone: str = Field(min_length=6)
    code: str | None = Field(default=None, min_length=1)
    password: str | None = Field(default=None, min_length=1)


class AuthChangeCodeRequest(BaseModel):
    code: str | None = Field(default=None, min_length=1)
    password: str | None = Field(default=None, min_length=1)
    newCode: str | None = Field(default=None, min_length=1)
    newPassword: str | None = Field(default=None, min_length=1)


class AuthOkResponse(BaseModel):
    ok: Literal[True]
    name: str


class AuthCodeNotSetResponse(BaseModel):
    ok: Literal[False]
    reason: Literal["CODE_NOT_SET"]


class MeAnonymous(BaseModel):
    authenticated: Literal[False]


class MeAuthenticated(BaseModel):
    authenticated: Literal[True]
    id: UUID
    phone: str
    name: str
    avatar: str | None
    isAdmin: bool


class AdminResetCodeRequest(BaseModel):
    phone: str = Field(min_length=6)
    newCode: str | None = Field(default=None, min_length=1)
    newPassword: str | None = Field(default=None, min_length=1)


class AdminGroupInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=300)


class AdminGroup(AdminGroupInput):
    id: UUID


class AdminWhitelistUpsertRequest(BaseModel):
    phone: str = Field(min_length=6)
    name: str = Field(min_length=1, max_length=120)


class AdminWhitelistUpdateRequest(BaseModel):
    currentPhone: str = Field(min_length=6)
    phone: str = Field(min_length=6)
    name: str = Field(min_length=1, max_length=120)


class AdminWhitelistGroupsRequest(BaseModel):
    groupIds: list[UUID] = Field(max_length=200)


class AdminWhitelistGroup(BaseModel):
    id: UUID
    name: str


class AdminWhitelistItem(BaseModel):
    userId: UUID
    phone: str
    name: str
    groups: list[AdminWhitelistGroup]


class AdminWhitelistResponse(BaseModel):
    items: list[AdminWhitelistItem]
    groups: list[AdminWhitelistGroup]


class User(BaseModel):
    id: UUID
    phone: str
    name: str
    avatar: str | None = None


class UserProfile(User):
    createdAt: datetime | None = None
    updatedAt: datetime | None = None


class UpdateUserProfileRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=30)
    avatar: str | None = None


class ContactItem(BaseModel):
    phone: str
    name: str
    avatar: str | None = None
    userId: UUID | None = None
    lastSeenAt: datetime | None = None


class ChatMember(BaseModel):
    id: UUID
    name: str
    phone: str
    avatar: str | None = None
    lastSeenAt: datetime | None = None
    role: Literal["ADMIN", "MEMBER"]


class PinnedMessageSender(BaseModel):
    id: UUID
    name: str
    avatar: str | None = None


class PinnedMessage(BaseModel):
    id: UUID
    text: str | None
    sender: PinnedMessageSender
    createdAt: datetime


class CreateDirectChatRequest(BaseModel):
    phone: str = Field(min_length=8)


class CreateGroupChatRequest(BaseModel):
    title: str = Field(min_length=1, max_length=30)
    participantsPhones: list[str] | None = Field(default=None, max_length=99)


class UpdateChatRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=30)
    avatar: str | None = Field(default=None, max_length=8388608)


class ChatUpdateResponse(BaseModel):
    ok: Literal[True]
    chatId: UUID
    title: str | None = None
    avatar: str | None = None
    updatedAt: datetime


class PinChatRequest(BaseModel):
    pinned: bool


class PinChatResponse(BaseModel):
    ok: Literal[True]
    chatId: UUID
    pinned: bool


class MuteChatRequest(BaseModel):
    muted: bool


class MuteChatResponse(BaseModel):
    ok: Literal[True]
    chatId: UUID
    muted: bool


class AddChatMemberRequest(BaseModel):
    phone: str = Field(min_length=8)


class AddChatMemberResponse(BaseModel):
    chatId: UUID
    userId: UUID
    role: Literal["ADMIN", "MEMBER"]


class MessagePreview(BaseModel):
    id: UUID
    text: str | None
    isDeleted: bool
    sender: User


class ForwardedMessagePreview(BaseModel):
    id: UUID
    sender: User


class ReadReceipt(BaseModel):
    userId: UUID
    readAt: datetime | None = None


class UserMessageMention(BaseModel):
    type: Literal["user"]
    userId: UUID
    displayName: str
    start: int = Field(ge=0)
    length: int = Field(ge=1)


class AllMessageMention(BaseModel):
    type: Literal["all"]
    start: int = Field(ge=0)
    length: int = Field(ge=1)


MessageMention = UserMessageMention | AllMessageMention


class AttachmentInput(BaseModel):
    key: str
    filename: str
    mimeType: str
    size: int = Field(ge=0, le=10485760)
    url: str
    width: int | None = None
    height: int | None = None


class FileRef(AttachmentInput):
    id: UUID


class ReactionUser(BaseModel):
    id: UUID
    name: str
    avatar: str | None = None


class Reaction(BaseModel):
    id: UUID
    emoji: str
    user: ReactionUser


class PollVote(BaseModel):
    userId: UUID


class PollOption(BaseModel):
    id: UUID
    text: str
    votes: list[PollVote]


class PollInput(BaseModel):
    question: str = Field(min_length=1, max_length=300)
    multi: bool | None = False
    options: list[str] = Field(min_length=2, max_length=12)


class Poll(BaseModel):
    id: UUID
    question: str
    multi: bool
    options: list[PollOption]


class Message(BaseModel):
    id: UUID
    relativeId: int
    chatId: UUID
    senderId: UUID
    threadRootMessageId: UUID | None = None
    threadRootMessage: MessagePreview | None = None
    forwardedFromMessageId: UUID | None = None
    forwardedFromMessage: ForwardedMessagePreview | None = None
    text: str | None
    isDeleted: bool
    createdAt: datetime
    updatedAt: datetime | None = None
    editedAt: datetime | None = None
    sender: User
    reactions: list[Reaction]
    fileRefs: list[FileRef]
    fileRefsCount: int | None = Field(default=None, ge=0)
    poll: Poll | None = None
    readReceipts: list[ReadReceipt]
    mentions: list[MessageMention] | None = None


class SearchMessage(Message):
    pass


class Chat(BaseModel):
    id: UUID
    type: Literal["DIRECT", "GROUP"]
    title: str | None
    avatar: str | None = None
    muted: bool | None = None
    pinned: bool | None = None
    unreadCount: int | None = Field(default=None, ge=0)
    firstUnreadMessageId: UUID | None = None
    role: Literal["ADMIN", "MEMBER"]
    members: list[ChatMember]
    updatedAt: datetime
    lastMessage: Message | None = None
    pinnedMessage: PinnedMessage | None = None
    pinnedMessages: list[PinnedMessage] | None = None


class CreateMessageRequest(BaseModel):
    text: str | None = Field(default=None, max_length=4000)
    mentions: list[MessageMention] | None = None
    threadRootMessageId: UUID | None = None
    forwardedFromMessageId: UUID | None = None
    attachments: list[AttachmentInput] | None = None
    poll: PollInput | None = None


class UpdateMessageRequest(BaseModel):
    text: str | None = Field(default=None, max_length=4000)
    mentions: list[MessageMention] | None = None
    attachments: list[AttachmentInput] | None = None


class BatchAttachmentsRequest(BaseModel):
    chatId: UUID
    messageIds: list[UUID] = Field(min_length=1, max_length=25)


class ChatImageAttachment(FileRef):
    chatId: UUID
    messageId: UUID
    createdAt: datetime
    attachmentCreatedAt: datetime


class ChatImageAttachmentsPage(BaseModel):
    items: list[ChatImageAttachment]
    nextOffset: int = Field(ge=0)
    hasMore: bool


class ReactionRequest(BaseModel):
    emoji: str = Field(min_length=1, max_length=16)


class ForwardMessageRequest(BaseModel):
    targetChatId: UUID


class MarkChatReadResponse(BaseModel):
    ok: Literal[True]
    messageIds: list[UUID]
    readAt: datetime


class UnpinMessageResponse(BaseModel):
    ok: Literal[True]
    pinnedMessageId: UUID | None
    pinnedMessages: list[PinnedMessage]


class LinkPreview(BaseModel):
    url: str
    title: str
    description: str | None
    siteName: str | None
    image: str | None
    video: str | None
    videoMimeType: str | None


class CallHistoryChat(BaseModel):
    id: UUID
    title: str | None
    type: Literal["DIRECT", "GROUP"]
    avatar: str | None


class CallHistoryItem(BaseModel):
    id: UUID
    chatId: UUID
    status: Literal[
        "RINGING",
        "IN_PROGRESS",
        "COMPLETED",
        "DECLINED",
        "MISSED",
        "CANCELED",
        "FAILED",
    ]
    direction: Literal["incoming", "outgoing"]
    createdAt: datetime
    startedAt: datetime | None
    endedAt: datetime | None
    durationSec: int = Field(ge=0)
    peer: User | None
    joinedUserIds: list[UUID]
    participantCount: int = Field(ge=0)
    signalingAllowed: bool | None = None
    chat: CallHistoryChat


class StartCallRequest(BaseModel):
    chatId: UUID


class DeclineCallRequest(BaseModel):
    reason: Literal["busy"] | None = None


class WebPushKeys(BaseModel):
    p256dh: str
    auth: str


class WebPushSubscribeRequest(BaseModel):
    endpoint: str
    keys: WebPushKeys


class UiFlowLogRequest(BaseModel):
    scope: Literal["app", "sw", "boot", "media", "chat", "call"]
    event: str
    payload: dict[str, Any] | None = None
    href: str | None = None
    visibilityState: str | None = None
    reportedClientMode: Literal["pwa", "browser"] | None = None
    reportedClientPlatform: (
        Literal["ios", "android", "mac", "desktop", "unknown"] | None
    ) = None
    ts: datetime | None = None


class WsEnvelope(BaseModel):
    event: str
    payload: Any | None


class WsPresenceHeartbeatPayload(BaseModel):
    visible: bool
    activeChatId: UUID | None = None


class WsTypingPayload(BaseModel):
    chatId: UUID


class WsCallSignalPayload(BaseModel):
    callId: UUID
    toUserId: UUID
    sdp: str | None = None
    candidate: dict[str, Any] | None = None
