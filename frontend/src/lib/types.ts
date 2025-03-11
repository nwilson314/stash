export interface UserResponse {
    id: number;
    username: string;
    email: string;
}

export interface Token {
    access_token: string;
    token_type: string;
}
  
export interface AuthResponse {
    token: Token;
    user: UserResponse;
}

export interface Link {
    id: string;
    url: string;
    original_url?: string;
    title?: string;
    short_summary?: string;
    note?: string;
    read?: boolean;
    
    // Content metadata
    content_type?: ContentType;
    author?: string;
    duration?: number;  // Duration in seconds for media content
    thumbnail_url?: string;
    
    // Processing status
    processing_status?: ProcessingStatus;
    processing_error?: string;
    
    // Timestamps
    created_at?: string;
    updated_at?: string;
    processed_at?: string;
    
    // Relationships
    category_id?: number;
    category?: Category;
}

export enum ContentType {
    WEBPAGE = "webpage",
    YOUTUBE = "youtube",
    SPOTIFY = "spotify",
    TWITTER = "twitter",
    GITHUB = "github",
    PDF = "pdf",
    UNKNOWN = "unknown"
}

export enum ProcessingStatus {
    PENDING = "pending",
    PROCESSING = "processing",
    COMPLETE = "complete",
    ERROR = "error"
}

export interface Category {
    id: number;
    name: string;
    created_at?: string;
    updated_at?: string;
}

export enum LinkStatusTab {
    Read = 'read', 
    Unread = 'unread'
}