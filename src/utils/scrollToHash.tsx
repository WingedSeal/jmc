import { useEffect } from "react";

const scrollToId = (sectionId: string) => {
    const offsetTop = document.querySelector<HTMLElement>(
        `section#${sectionId}`
    )?.offsetTop;
    if (offsetTop === undefined) {
        return true;
    }
    window.scrollTo({
        top: offsetTop,
        behavior: "smooth",
    });
    return false;
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
        if (scrollToId(hash)) return;
    }, []);
};

export default useScrollToHash;
