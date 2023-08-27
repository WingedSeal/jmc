import React, { useEffect, useRef, useState } from "react";
import { ReactComponent as SearchSvg } from "../../assets/image/icon/magnifying_glass_solid.svg";
import { ReactComponent as ClearSvg } from "../../assets/image/icon/xmark_solid.svg";
import isDisplay from "../../utils/isDisplay";
import getDocsPages from "./DocsPages";

interface SidebarNavInterface {
    children?: React.ReactNode;
}

const SidebarNav: React.FC<SidebarNavInterface> = ({ children }) => {
    const [isOpen, setOpen] = useState(true);
    const [searchValue, setSearchValue] = useState("");
    const inputRef = useRef<HTMLInputElement>(null);
    useEffect(() => {
        if (window.outerWidth < 768)
            // 768px is md (phone)
            setOpen(false);
    }, []);
    return (
        <div className="flex">
            <div
                className={
                    "min-h-screen bg-gray-900" +
                    (!isOpen ? " w-0 md:w-0" : " w-full md:w-1/6")
                }
            />
            {isOpen ? (
                <div
                    className="cursor-pointer text-white mt-[calc(100vh-1.75rem)] md:mt-8 fixed z-30 ml-[calc(100%-1.75rem)] md:ml-[16.667%] w-7 h-7 bg-tertiary-contrast rounded-tl-lg md:rounded-none md:rounded-tr-lg md:rounded-br-lg"
                    onClick={() => setOpen(false)}
                >
                    <div className="m-auto text-center">{"<"}</div>
                </div>
            ) : (
                <div
                    className="cursor-pointer text-white mt-8 fixed z-30 w-7 h-7 bg-tertiary-contrast rounded-tr-lg rounded-br-lg"
                    onClick={() => setOpen(true)}
                >
                    <div className="m-auto text-center">{">"}</div>
                </div>
            )}
            <section
                className={
                    "bg-gray-900 min-h-screen max-h-screen w-full md:w-1/6 flex flex-col px-1 pl-4 md:px-3 pt-8 fixed overflow-y-auto transition-all duration-200 ease-out z-20" +
                    (!isOpen ? " scale-x-0 -translate-x-1/2" : "")
                }
            >
                <div>
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
                            className="absolute top-1/2 right-1 -translate-x-1/2 -translate-y-1/2 h-3/4 ml-auto cursor-pointer"
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
                    <div className="my-6" />
                </div>
            </section>
            <div className={isOpen ? "w-max md:w-5/6" : "w-full"}>
                {children}
            </div>
        </div>
    );
};

export default SidebarNav;
