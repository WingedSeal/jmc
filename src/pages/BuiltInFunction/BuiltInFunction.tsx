import React, { useRef, useState } from "react";
import BuildinFeatures from "./Features";
import { ReactComponent as SearchSvg } from "../../assets/image/icon/magnifying_glass_solid.svg";
import { ReactComponent as ClearSvg } from "../../assets/image/icon/xmark_solid.svg";
import useScrollToHash from "../../utils/scrollToHash";

const isDisplay = (summary: string, searchValue: string, keywords: string) => {
    summary = summary.toLowerCase();
    if (searchValue === "") {
        return true;
    }
    if (summary.includes(searchValue.toLowerCase())) {
        return true;
    }

    let terms = searchValue.match(/(?:[^\s"]+|"[^"]*")+/g); // Split searchValue into multiple terms
    if (terms === null) {
        terms = [searchValue];
    }

    for (let i = 0; i < terms.length; i++) {
        let value = terms[i].toLowerCase();

        if (
            value.length > 1 &&
            value.charAt(0) === '"' &&
            value.charAt(value.length - 1) === '"'
        ) {
            value = value.substring(1, value.length - 1);
        }
        if (summary.includes(value)) {
            return true;
        }
        if (keywords.includes(value)) {
            return true;
        }
    }
    return false;
};

const closeAll = () => {
    const features = document.querySelectorAll(".feature");
    features.forEach((feature) => {
        feature.removeAttribute("open");
    });
};

const BuiltInFunction = () => {
    useScrollToHash();
    const [searchValue, setSearchValue] = useState("");
    const inputRef = useRef<HTMLInputElement>(null);
    return (
        <section className="bg-secondary-dark min-h-screen w-screen flex flex-col px-2 md:px-10 pt-[17vh]">
            {/* Begin search bar */}
            <div className="relative h-12 mx-8 mb-8">
                <div
                    className="absolute top-0 left-0 w-12 h-full bg-tertiary z-20 cursor-pointer rounded-[50%] hover:bg-tertiary-contrast transition-all active:scale-105"
                    onClick={(e) => {
                        setSearchValue(inputRef.current!.value);
                        closeAll();
                    }}
                >
                    <SearchSvg className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 fill-white text-2xl" />
                </div>
                <input
                    ref={inputRef}
                    className="absolute top-0 left-0 w-full h-full pl-16 pr-4 py-2 rounded-[3rem] border-0 bg-gray-800 focus:!outline-none focus:shadow-[0_0_0.5rem_#ffaa00] text-white text-sm md:text-base"
                    type="text"
                    placeholder="Search..."
                    onKeyDown={(event) => {
                        if (event.key === "Enter") {
                            setSearchValue(
                                (event.target as HTMLInputElement).value
                            );
                            closeAll();
                        }
                    }}
                />
                <div
                    className="absolute top-1/2 right-4 -translate-x-1/2 -translate-y-1/2 h-3/4 ml-auto"
                    onClick={() => {
                        inputRef.current!.value = "";
                        inputRef.current!.focus();
                        setSearchValue("");
                    }}
                >
                    <ClearSvg className="fill-gray-200 h-full" />
                </div>
            </div>
            {/* End search bar */}
            {BuildinFeatures.map(
                (BuildinFeature, i) =>
                    isDisplay(
                        BuildinFeature.props.summary,
                        searchValue,
                        BuildinFeature.props.keywords
                    ) && <div key={i}>{BuildinFeature}</div>
            )}
        </section>
    );
};

export default BuiltInFunction;
