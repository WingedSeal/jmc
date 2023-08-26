import { useEffect } from "react";

const scrollToId = (sectionId: string) => {
    const offsetTop = document.querySelector<HTMLElement>(
        `section#${sectionId}`
    )?.offsetTop;
    if (offsetTop === undefined) {
        return false;
    }
    window.scrollTo({
        top: offsetTop,
        behavior: "smooth",
    });
    return true;
};

const focusOnDetails = (sectionId: string) => {
    const element = document.querySelector<HTMLDetailsElement>(
        `details#${sectionId}`
    );
    if (element === null) return;
    element.open = true;
};

// function removeHash() {
//     window.history.pushState(
//         "",
//         document.title,
//         window.location.pathname + window.location.search
//     );
// }

const useScrollToHash = () => {
    useEffect(() => {
        const hash = window.location.hash.substring(1);
        if (!hash) return;
        if (scrollToId(hash))
            setTimeout(() => {
                focusOnDetails(hash);
            }, 700);
    }, []);
};

export default useScrollToHash;
