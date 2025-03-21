import React from "react";

// Define language options with flag emojis
export const LANGUAGE_OPTIONS = [
  { value: "EN", label: "🇺🇸 English" },
  { value: "HI", label: "🇮🇳 Hindi" },
  { value: "PT", label: "🇵🇹 Portuguese" },
  { value: "ZH", label: "🇨🇳 Mandarin (Chinese)" },
  { value: "ES", label: "🇪🇸 Spanish" },
  { value: "FR", label: "🇫🇷 French" },
  { value: "DE", label: "🇩🇪 German" },
  { value: "JP", label: "🇯🇵 Japanese" },
  { value: "AR", label: "🇦🇪 Arabic" },
  { value: "RU", label: "🇷🇺 Russian" },
  { value: "KR", label: "🇰🇷 Korean" },
  { value: "ID", label: "🇮🇩 Indonesian" },
  { value: "IT", label: "🇮🇹 Italian" },
  { value: "NL", label: "🇳🇱 Dutch" },
  { value: "TR", label: "🇹🇷 Turkish" },
  { value: "PL", label: "🇵🇱 Polish" },
  { value: "SV", label: "🇸🇪 Swedish" },
  { value: "TL", label: "🇵🇭 Tagalog (Filipino)" },
  { value: "MS", label: "🇲🇾 Malay" },
  { value: "RO", label: "🇷🇴 Romanian" },
  { value: "UK", label: "🇺🇦 Ukrainian" },
  { value: "EL", label: "🇬🇷 Greek" },
  { value: "CS", label: "🇨🇿 Czech" },
  { value: "DA", label: "🇩🇰 Danish" },
  { value: "FI", label: "🇫🇮 Finnish" },
  { value: "BG", label: "🇧🇬 Bulgarian" },
  { value: "HR", label: "🇭🇷 Croatian" },
  { value: "SK", label: "🇸🇰 Slovak" },
  { value: "TA", label: "🇮🇳 Tamil" },
];

export interface DubbingStatus {
  [segmentId: string]: {
    [language: string]: string;
  };
}

interface LanguageSelectorProps {
  segmentId: string;
  onSelectLanguage: (segmentId: string, languageCode: string) => void;
  dubbingStatus: DubbingStatus;
  selectedLanguage?: string;
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  segmentId,
  onSelectLanguage,
  dubbingStatus,
  selectedLanguage,
}) => {
  return (
    <div className="bg-ai-darker border border-ai-lighter rounded-md p-2 animate-in fade-in zoom-in duration-200">
      <p className="text-xs text-white mb-1">Select language for dubbing:</p>
      <div className="grid grid-cols-2 gap-1 max-h-[200px] overflow-y-auto">
        {LANGUAGE_OPTIONS.map((lang) => {
          const isProcessing =
            dubbingStatus[segmentId]?.[lang.label] === "processing";
          const isCompleted =
            dubbingStatus[segmentId]?.[lang.label] === "completed";
          const isFailed = dubbingStatus[segmentId]?.[lang.label] === "failed";
          const isSelected = selectedLanguage === lang.label;

          return (
            <button
              key={lang.value}
              onClick={() => onSelectLanguage(segmentId, lang.label)}
              disabled={lang.value === "EN" || isProcessing}
              className={`text-xs px-2 py-1 rounded flex items-center justify-between
                ${
                  lang.value === "EN"
                    ? "bg-ai-lighter text-ai-muted cursor-not-allowed"
                    : ""
                }
                ${
                  isProcessing ? "bg-blue-500/30 text-blue-300 cursor-wait" : ""
                }
                ${isCompleted ? "bg-green-500/30 text-green-300" : ""}
                ${isFailed ? "bg-red-500/30 text-red-300" : ""}
                ${
                  isSelected && !isProcessing && !isCompleted && !isFailed
                    ? "bg-ai-accent text-white"
                    : ""
                }
                ${
                  !isSelected &&
                  !isProcessing &&
                  !isCompleted &&
                  !isFailed &&
                  lang.value !== "EN"
                    ? "bg-ai-accent/50 text-white hover:bg-ai-accent/80"
                    : ""
                }
              `}
            >
              <span>{lang.label}</span>
              {isProcessing && (
                <div className="h-3 w-3 rounded-full border-2 border-blue-400 border-t-transparent animate-spin ml-1"></div>
              )}
              {isCompleted && (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-3 w-3 text-green-400 ml-1"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
              {isFailed && (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-3 w-3 text-red-400 ml-1"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default LanguageSelector;
