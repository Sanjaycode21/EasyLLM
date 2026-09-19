import { AIPlatformProvider } from "./types";
import { APIProvider } from "./api_provider";
import { LocalProvider } from "./local_provider";

export const apiProvider = new APIProvider();
export const localProvider = new LocalProvider();

export function getProvider(useLocal: boolean = false): AIPlatformProvider {
  return useLocal ? localProvider : apiProvider;
}

export * from "./types";
