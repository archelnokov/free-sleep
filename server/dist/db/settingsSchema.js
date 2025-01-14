// WARNING! - Any changes here MUST be the same between app/src/api & server/src/db/
import { z } from 'zod';
import { TIME_ZONES } from './timeZones.js';
import { TimeSchema } from './schedulesSchema.js';
export const TEMPERATURES = ['celsius', 'fahrenheit'];
const Temperatures = z.enum(TEMPERATURES);
const SideSettingsSchema = z.object({
    awayMode: z.boolean(),
}).strict();
export const SettingsSchema = z.object({
    timeZone: z.enum(TIME_ZONES).nullable(),
    left: SideSettingsSchema,
    right: SideSettingsSchema,
    primePodDaily: z.object({
        enabled: z.boolean(),
        time: TimeSchema,
    }),
    temperatureFormat: Temperatures,
}).strict();
