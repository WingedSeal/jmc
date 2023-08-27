import React, { useRef, useState } from "react";
import { ReactComponent as SearchSvg } from "../../assets/image/icon/magnifying_glass_solid.svg";
import { ReactComponent as ClearSvg } from "../../assets/image/icon/xmark_solid.svg";
import isDisplay from "../../utils/isDisplay";
import getDocsPages from "./DocsPages";

interface SidebarNavInterface {
    children?: React.ReactNode;
}

const SidebarNav: React.FC<SidebarNavInterface> = ({ children }) => {
    const [searchValue, setSearchValue] = useState("");
    const inputRef = useRef<HTMLInputElement>(null);
    return (
        <div className="flex">
            <div className="min-h-screen w-1/6" />
            <section className="bg-gray-900 min-h-screen w-1/6 flex flex-col px-1 md:px-3 pt-[13vh] fixed overflow-y-auto">
                <p className="text-gray-400">
                    this sidebar nav is under construction but im publishing it
                    anyway, wat u gonna do about it{" "}
                </p>
                {/* Begin search bar */}
                <div className="relative h-6 mx-0 mb-4">
                    <div
                        className="absolute top-0 left-0 w-6 h-full bg-tertiary z-20 cursor-pointer rounded-[50%] hover:bg-tertiary-contrast transition-all active:scale-105"
                        onClick={(e) => {
                            setSearchValue(inputRef.current!.value);
                        }}
                    >
                        <SearchSvg className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 fill-white text-2xl" />
                    </div>
                    <input
                        ref={inputRef}
                        className="absolute top-0 left-0 w-full h-full pl-8 pr-6 py-2 rounded-[3rem] border-0 bg-gray-800 focus:!outline-none focus:shadow-[0_0_0.5rem_#ffaa00] text-white text-sm md:text-base"
                        type="text"
                        placeholder="Search..."
                        onKeyDown={(event) => {
                            if (event.key === "Enter") {
                                setSearchValue(
                                    (event.target as HTMLInputElement).value
                                );
                            }
                        }}
                    />
                    <div
                        className="absolute top-1/2 right-1 -translate-x-1/2 -translate-y-1/2 h-3/4 ml-auto"
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
                {getDocsPages(searchValue).map(
                    (DocsLink, i) =>
                        (isDisplay(
                            DocsLink.props.name,
                            searchValue,
                            DocsLink.props.keyword
                        ) ||
                            DocsLink.props.sections) && (
                            <div key={i}>{DocsLink}</div>
                        )
                )}
            </section>
            <div className="w-5/6">{children}</div>
        </div>
    );
};

export default SidebarNav;
