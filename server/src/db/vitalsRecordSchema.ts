import { z } from 'zod';

export const vitalsRecordSchema = z.object({
  side: z.enum(['right', 'left']),
  period_start: z.number().int(), // Epoch timestamp
  heart_rate: z.number().int().min(30).max(90),
  hrv: z.number().int().min(0).max(200),
  breathing_rate: z.number().int().min(5).max(30), // Normal breathing rate range
});

export type VitalsRecord = z.infer<typeof vitalsRecordSchema>;

