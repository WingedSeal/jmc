import React, { useEffect, useRef, useState } from "react";
import { loadPyodide, PyodideInterface } from "pyodide";
import CodeBlock from "../../components/CodeBlock";
import { useSearchParams } from "react-router-dom";
import lzString from "lz-string";
const getPyodide = async () => {
    const pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.22.1/full/",
    });
    // const consoleLog = console.log;
    // console.log = () => {};
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install("jmcfunction", false, true, null, true);
    // console.log = consoleLog;
    return pyodide;
};

const loadingMsg =
    "The compiler is still loading, please wait a moment.\nCompilation will start once the compiler is loaded.";

const TryOut = () => {
    const [pyodide, setPyodide] = useState<PyodideInterface>();
    const [JMCVersion, setJMCVersion] = useState("");
    const [JMCResult, setJMCResult] = useState<Map<string, string>>(new Map());
    const [JMCError, setJMCError] = useState("");
    const [isError, setIsError] = useState(false);
    const [isShowHeader, setIsShowHeader] = useState(false);
    const [shareText, setShareText] = useState("SHARE");
    const namespaceInput = useRef<HTMLInputElement>(null);
    const contentTextArea = useRef<HTMLTextAreaElement>(null);
    const contentHeaderArea = useRef<HTMLTextAreaElement>(null);
    const [params, setParams] = useSearchParams();
    let copiedTimeout: NodeJS.Timeout;
    let shareTimeout: NodeJS.Timeout;
    useEffect(() => {
        let namespace = params.get("namespace");
        let jmc = params.get("jmc");
        let header = params.get("header");
        if (namespace)
            namespaceInput.current!.value =
                lzString.decompressFromEncodedURIComponent(namespace);
        if (jmc)
            contentTextArea.current!.value =
                lzString.decompressFromEncodedURIComponent(jmc);
        if (header)
            contentHeaderArea.current!.value =
                lzString.decompressFromEncodedURIComponent(header);
        if (namespace || jmc || header) compile();
        setParams(new URLSearchParams());
        getPyodide().then((pyodide) => {
            setPyodide(pyodide);
            pyodide.runPython(
                "from jmc.api import VERSION, EXCEPTIONS;from jmc import JMCTestPack"
            );
            setJMCVersion(pyodide.globals.get("VERSION"));
        });
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    useEffect(() => {
        if (JMCError === loadingMsg) {
            compile();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [pyodide]);

    const compile = () => {
        if (pyodide === undefined) {
            setIsError(true);
            setJMCError(loadingMsg);
            return;
        }
        pyodide.globals.set(
            "NAMESPACE",
            namespaceInput.current!.value
                ? namespaceInput.current!.value
                : namespaceInput.current!.placeholder
        );
        pyodide.globals.set("JMC_FILE", contentTextArea.current!.value);
        pyodide.globals.set("HEADER_FILE", contentHeaderArea.current!.value);
        pyodide.runPython(
            `
try:
    BUILT = JMCTestPack(namespace=NAMESPACE, output=".").set_jmc_file(JMC_FILE).set_header_file(HEADER_FILE).built
except EXCEPTIONS as error:
    BUILT = {}
    ERROR = type(error).__name__ + "\\n" + str(error)`
        );
        const built: Map<string, string> = pyodide.globals.get("BUILT").toJs();
        if (built.size === 0) {
            setIsError(true);
            setJMCError(
                pyodide.globals
                    .get("ERROR")
                    .replace(new RegExp("/home/pyodide/", "g"), "")
            );
        } else {
            setIsError(false);
            setJMCResult(built);
        }
    };

    return (
        <>
            <section className="min-h-screen bg-primary-dark flex flex-wrap pt-[12vh] pb-5 md:pt-[13vh] px-4 md:px-11 flex-col items-centers content-center relative">
                <div className="mx-auto flex flex-col items-centers content-center relative w-[80vw]">
                    <div className="flex">
                        <img
                            className="h-12 mr-2 md:h-14 md:mr-5 my-auto"
                            src={require("../../assets/image/jmc_icon.png")}
                            alt="JMC-icon"
                        />
                        {JMCVersion === "" ? (
                            <h2 className="text-[#FFAA00] text-xl md:text-6xl mr-auto line">
                                Loading JMC Compiler...
                            </h2>
                        ) : (
                            <h2 className="text-primary text-xl md:text-6xl mr-auto line">
                                JMC Compiler{" "}
                                <span className="inline-block">
                                    {JMCVersion}
                                </span>
                            </h2>
                        )}
                    </div>
                    <div className="relative my-1 md:my-2 min-w-[80vw] max-w-full">
                        <input
                            ref={namespaceInput}
                            placeholder="namespace"
                            className="bg-[#292D3E] rounded-md md:rounded-2xl text-[#eeffff] px-4 py-1 md:px-8 md:py-3 min-w-[80vw] max-w-full"
                            onChange={() => {}}
                            spellCheck="false"
                        />
                        <button
                            className="aspect-square min-h-full absolute top-[160%] right-full rounded-tl-md rounded-bl-md p-2 bg-[#292D3E]"
                            onClick={() => {
                                setIsShowHeader(!isShowHeader);
                            }}
                        >
                            <img
                                className="h-full w-full"
                                src={require("../../assets/image/jmc_icon192.png")}
                                alt="JMC-icon"
                                hidden={isShowHeader}
                            />
                            <img
                                className="h-full w-full"
                                src={require("../../assets/image/hjmc_icon192.png")}
                                alt="JMC-icon"
                                hidden={!isShowHeader}
                            />
                        </button>
                    </div>

                    <textarea
                        ref={contentHeaderArea}
                        className="mt-1 md:mt-2 bg-[#292D3E] rounded-md md:rounded-2xl text-[#eeffff] px-4 py-1 md:px-8 md:py-3 min-h-[60vh] max-w-full z-[1]"
                        placeholder="Header File"
                        spellCheck="false"
                        hidden={!isShowHeader}
                        onKeyDown={(e) => {
                            if (e.key === "Tab") {
                                e.preventDefault();
                                const start =
                                    contentHeaderArea.current!.selectionStart;
                                const end =
                                    contentHeaderArea.current!.selectionEnd;
                                contentHeaderArea.current!.value =
                                    contentHeaderArea.current!.value.substring(
                                        0,
                                        start
                                    ) +
                                    "\t" +
                                    contentHeaderArea.current!.value.substring(
                                        end
                                    );
                                contentHeaderArea.current!.selectionStart =
                                    contentHeaderArea.current!.selectionEnd =
                                        start + 1;
                            }
                        }}
                    />
                    <textarea
                        ref={contentTextArea}
                        className="mt-1 md:mt-2 bg-[#292D3E] rounded-md md:rounded-2xl text-[#eeffff] px-4 py-1 md:px-8 md:py-3 min-h-[60vh] max-w-full z-[1]"
                        spellCheck="false"
                        placeholder="JMC File"
                        hidden={isShowHeader}
                        onKeyDown={(e) => {
                            if (e.key === "Tab") {
                                e.preventDefault();
                                const start =
                                    contentTextArea.current!.selectionStart;
                                const end =
                                    contentTextArea.current!.selectionEnd;
                                contentTextArea.current!.value =
                                    contentTextArea.current!.value.substring(
                                        0,
                                        start
                                    ) +
                                    "\t" +
                                    contentTextArea.current!.value.substring(
                                        end
                                    );
                                contentTextArea.current!.selectionStart =
                                    contentTextArea.current!.selectionEnd =
                                        start + 1;
                            }
                        }}
                    />
                    <div className="mx-auto mt-1 relative">
                        <button
                            onClick={compile}
                            className="text-2xl tracking-widest font-bold mx-auto w-[50vw] h-[6vh] text-primary-dark bg-primary rounded-lg border-r-4 border-b-4 border-gray-300 hover:scale-x-[1.02] active:scale-x-[0.98] active:border-r-2 active:border-b-2 transition-all"
                        >
                            Compile
                        </button>
                        <button
                            className="absolute top-1/2 left-full -translate-y-1/2 translate-x-1/4 md:translate-x-1/2 bg-slate-900 text-tertiary p-2 tracking-wide rounded-md hover:scale-105 transition-all active:scale-95"
                            onClick={() => {
                                let namespace =
                                    lzString.compressToEncodedURIComponent(
                                        namespaceInput.current!.value
                                    );
                                let jmc =
                                    lzString.compressToEncodedURIComponent(
                                        contentTextArea.current!.value
                                    );
                                let header =
                                    lzString.compressToEncodedURIComponent(
                                        contentHeaderArea.current!.value
                                    );
                                const ENCODED_EMPTY_STR = "Q";
                                if (namespace !== ENCODED_EMPTY_STR)
                                    params.set("namespace", namespace);
                                else params.delete("namespace");
                                if (jmc !== ENCODED_EMPTY_STR)
                                    params.set("jmc", jmc);
                                else params.delete("jmc");
                                if (header !== ENCODED_EMPTY_STR)
                                    params.set("header", header);
                                else params.delete("header");
                                const paramsString = params.toString();
                                if (paramsString.length > 1900) {
                                    alert(
                                        `The content is too big to share! (${Number(
                                            paramsString.length / 19
                                        ).toFixed(2)}% of the limit)`
                                    );
                                } else {
                                    navigator.clipboard.writeText(
                                        window.location.href +
                                            "?" +
                                            paramsString
                                    );
                                    if (copiedTimeout)
                                        clearTimeout(copiedTimeout);
                                    if (shareTimeout)
                                        clearTimeout(shareTimeout);
                                    copiedTimeout = setTimeout(() => {
                                        setShareText("Copied");
                                    }, 200);
                                    shareTimeout = setTimeout(() => {
                                        setShareText("SHARE");
                                    }, 3000);
                                }
                            }}
                        >
                            {shareText}
                        </button>
                    </div>
                </div>
                <div className="mt-8 max-w-full" hidden={isError}>
                    {/* No Error */}
                    {Object.keys(Object.fromEntries(JMCResult)).map((key) => {
                        return (
                            <div key={key}>
                                <div className="bg-gray-900 text-sm md:text-xl text-primary-contrast p-2 rounded-sm">
                                    {">"} {key}
                                </div>
                                <CodeBlock>
                                    <pre className="inline text-sm md:text-lg">
                                        {JMCResult.get(key)}
                                    </pre>
                                </CodeBlock>
                            </div>
                        );
                    })}
                </div>
                <div className="text-white max-w-full" hidden={!isError}>
                    {/* Error */}
                    <CodeBlock>
                        <pre className="text-warning inline font-mono text-sm md:text-xl">
                            {JMCError}
                        </pre>
                    </CodeBlock>
                </div>
            </section>
        </>
    );
};

export default TryOut;
