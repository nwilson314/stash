export interface Link {
    id: string;
    url: string;
    note?: string;
    read?: boolean;
}

export enum LinkStatusTab {
    Read = 'read', 
    Unread = 'unread'
}