"""SQLAlchemy models — import all for Alembic autogenerate."""

from database.models.auth import (
    EmailVerificationToken, LoginHistory, NotificationSetting, OAuthAccount, PasswordHistory, PasswordResetToken,
    TwoFactorAuth, User, UserActivity, UserPreference, UserProfile, UserSession,
)
from database.models.tenant import (
    ApiKey, BillingAccount, Department, FeatureFlag, Invitation, Organization,
    OrganizationFeatureFlag, OrganizationMember, Permission, Role, RolePermission,
    Subscription, SubscriptionPlan, Team, TeamMember, UserRole, Workspace,
)
from database.models.customer import (
    Customer, CustomerAddress, CustomerAISummary, CustomerAttachment, CustomerBusinessDetail,
    CustomerCommunication, CustomerLifecycleEvent, CustomerNote, CustomerScore,
    CustomerSegmentMember, CustomerSocialProfile, CustomerTag, Segment, Tag,
)
from database.models.commerce import (
    Coupon, CouponRedemption, CustomerSubscription, Invoice, InvoiceItem, Order, OrderItem,
    Payment, Product, ProductCategory, Refund, ShippingRecord, TaxRate,
)
from database.models.behavior import (
    ClickEvent, CustomerEvent, CustomerJourney, Funnel, FunnelStep, JourneyTouchpoint,
    PageView, ScrollEvent, SearchEvent, WebSession,
)
from database.models.marketing import (
    ABTest, ABTestVariant, AttributionEvent, AttributionModel, Audience, AudienceMember,
    Campaign, CampaignMetric, EmailCampaign, PushCampaign, SmsCampaign, WhatsappCampaign,
)
from database.models.sales import (
    Deal, Lead, LeadScore, LeadSource, Meeting, PipelineStage, SalesActivity,
    SalesForecast, SalesTask,
)
from database.models.support import (
    ChatMessage, CSATResponse, Feedback, KnowledgeBaseArticle, LiveChat, NPSResponse,
    Rating, Review, SupportTicket, TicketMessage,
)
from database.models.ai import (
    AIConversation, AIExplanation, AIForecast, AIInsight, AIMessage, AIPrediction,
    AIRecommendation, AIReport, Embedding, KnowledgeBaseDocument, MLModelVersion,
    PromptHistory, PromptTemplate, VectorMetadata,
)
from database.models.ml import (
    DriftDetectionLog, FeatureMetadata, FeatureStoreEntry, MLExperiment,
    MLEvaluationMetric, MLInferenceLog, MLModel, MLPredictionResult, MLTrainingDataset,
    ModelMonitoringMetric,
)
from database.models.analytics import (
    AnalyticsAggregation, AnalyticsSnapshot, DashboardCache, KPISnapshot,
    MaterializedViewRefreshLog,
)
from database.models.reporting import (
    Report, ReportExport, ReportShare, ReportTemplate, ReportVersion, ScheduledReport,
)
from database.models.notifications import (
    Notification, NotificationChannelConfig, NotificationDeliveryLog, NotificationTemplate,
)
from database.models.integrations import Integration, IntegrationCredential, SyncLog, WebhookEvent
from database.models.security import (
    AccessLog, ApiToken, AuditLog, EncryptionMetadata, PermissionLog, RefreshToken,
    SecurityEvent,
)
from database.models.files import AIFile, Document, FileExport, FileUpload, Image, TempFile
from database.models.system import (
    AppSetting, Country, Currency, Language, OrganizationSetting, SystemLog, Theme,
)

__all__ = [
    "Organization", "Workspace", "User", "Customer", "Order", "Campaign", "Deal",
    "AIConversation", "Report", "Integration", "AuditLog", "FileUpload",
]
