import { useEffect } from "react";
import closeNavBarEvent from "./events/closeNavBar";

export const scrollToId = (sectionId: string) => {
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
    setTimeout(() => {
        if (Math.abs(window.scrollY - offsetTop) <= 1)
            window.dispatchEvent(closeNavBarEvent);
    }, 300 + Math.abs(offsetTop - window.scrollY) * 0.5);
    return true;
};

export const focusOnDetails = (sectionId: string) => {
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

export const scrollToHash = (hash: string | null = null) => {
    hash ??= window.location.hash.substring(1);
    if (!hash) return;
    if (scrollToId(hash))
        setTimeout(() => {
            focusOnDetails(hash!);
        }, 700);
};

const useScrollToHash = () => {
    useEffect(scrollToHash, []);
};

export default useScrollToHash;
