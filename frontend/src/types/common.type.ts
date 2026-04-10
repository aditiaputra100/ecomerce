export interface SuccessResponse<T, S = null> {
  message: string
  data: T
  metadata: S | null
}
