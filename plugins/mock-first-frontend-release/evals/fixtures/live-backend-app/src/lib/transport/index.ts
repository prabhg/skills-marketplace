// GraphQL transport: bearer token from the auth provider; throws ApiError by taxonomy. Endpoint from VITE_API_URL (non-production).
export declare const transport: { request<T>(doc: string, vars?: Record<string, unknown>): Promise<T> };
