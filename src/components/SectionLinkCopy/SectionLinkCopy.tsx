import { useState } from "react";

interface SectionLinkCopyProps {
    sectionId: string;
}

const SectionLinkCopy: React.FC<SectionLinkCopyProps> = ({ sectionId }) => {
    const [copiedTimer, setCopiedTimer] = useState<NodeJS.Timeout | null>(null);

    const handleCopy = (e: React.MouseEvent): void => {
        e.preventDefault();
        const url = window.location.href.split("#")[0] + "#" + sectionId;
        navigator.clipboard.writeText(url);

        if (copiedTimer) {
            clearTimeout(copiedTimer);
        }

        const timer = setTimeout(() => setCopiedTimer(null), 2000);
        setCopiedTimer(timer);
    };

    return (
        <button
            onClick={handleCopy}
            className="cursor-pointer md:text-xl text-white text-sm"
            type="button"
        >
            {copiedTimer ? "\u00A0✓" : "🔗"}
        </button>
    );
};

export default SectionLinkCopy;
