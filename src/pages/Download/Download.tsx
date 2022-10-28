import React from "react";
import { ReactComponent as DownloadSvg } from "../../assets/image/download_icon.svg";
import { ReactComponent as WindowsSvg } from "../../assets/image/windows.svg";
import { ReactComponent as PythonSvg } from "../../assets/image/python.svg";

const Download = () => {
    return (
        <>
            <section className="min-h-screen bg-primary-dark flex flex-wrap pt-[14vh] md:pt-[15vh] px-2 md:px-10 flex-col items-centers">
                <div className="text-primary text-3xl md:text-6xl mx-auto text-center">
                    Download JMC Compiler
                </div>
                <div className="text-primary-contrast text-lg md:text-3xl mx-auto mt-2 md:mt-4 text-center">
                    Free and open-source compiler for JavaScript-like Minecraft
                    Function
                </div>
                <div className="flex flex-row flex-wrap justify-evenly mt-4 md:mt-[10vh]">
                    <div className="flex flex-col flex-nowrap items-center m-8">
                        <WindowsSvg className="mb-4 md:mb-8 h-[min(20vh,30vw)]" />
                        <a
                            href="https://github.com/WingedSeal/jmc/releases/latest/download/JMC.exe"
                            rel="noreferrer"
                            className="h-16 w-44 md:h-24 md:w-72 bg-tertiary flex text-black font-bold text-lg md:text-3xl hover:bg-tertiary-contrast"
                        >
                            <h2 className="m-auto flex">
                                <DownloadSvg className="h-[1.5rem] mr-3" />
                                Executable
                            </h2>
                        </a>
                    </div>
                    <div className="flex flex-col flex-nowrap items-center m-8">
                        <PythonSvg className="mb-4 md:mb-8 h-[min(20vh,30vw)]" />
                        <a
                            href="https://github.com/WingedSeal/jmc/releases/latest"
                            target="_blank"
                            rel="noreferrer"
                            className="h-16 w-44 md:h-24 md:w-72 bg-tertiary flex text-black font-bold text-lg md:text-3xl hover:bg-tertiary-contrast"
                        >
                            <h2 className="m-auto flex">
                                <DownloadSvg className="h-[1.5rem] mr-3" />
                                Python
                            </h2>
                        </a>
                    </div>
                </div>
            </section>
        </>
    );
};
export default Download;
