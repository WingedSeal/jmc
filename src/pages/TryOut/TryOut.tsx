import React, { useEffect, useRef, useState } from "react";
import { loadPyodide, PyodideInterface } from "pyodide";
import LoadingScreen from "../../components/LoadingScreen";

const getPyodide = async () => {
    const pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.22.1/full/",
    });
    const consoleLog = console.log;
    console.log = () => {};
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install("jmcfunction", false, true, null, true);
    console.log = consoleLog;
    return pyodide;
};

const TryOut = () => {
    const [isLoaded, setIsLoaded] = useState(false);
    const [pyodide, setPyodide] = useState<PyodideInterface>();
    const [JMCVersion, setJMCVersion] = useState("");
    const [JMCResult, setJMCResult] = useState<Map<string, string>>(new Map());
    const [JMCError, setJMCError] = useState("");
    const [isError, setIsError] = useState(false);
    const namespaceInput = useRef<HTMLInputElement>(null);
    const contentTextArea = useRef<HTMLTextAreaElement>(null);
    const contentHeaderArea = useRef<HTMLTextAreaElement>(null);
    useEffect(() => {
        getPyodide().then((pyodide) => {
            setPyodide(pyodide);
            setIsLoaded(true);
            pyodide.runPython(
                "from jmc.api import VERSION, EXCEPTIONS;from jmc import JMCTestPack"
            );
            setJMCVersion(pyodide.globals.get("VERSION"));
        });
    }, []);

    return (
        <>
            <LoadingScreen isLoaded={isLoaded} />
            <section className="min-h-screen bg-primary-dark flex flex-wrap pt-[14vh] pb-5 md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
                {" "}
                <p className="text-white">{JMCVersion}</p>
                <input
                    ref={namespaceInput}
                    defaultValue="namespace"
                    className="mb-2"
                    onChange={() => {}}
                />
                <textarea
                    ref={contentHeaderArea}
                    className="w-4/5 h-[60vh] mb-4"
                    placeholder="Header"
                    onKeyDown={(e) => {
                        if (e.key === "Tab") {
                            e.preventDefault();
                            const start =
                                contentHeaderArea.current!.selectionStart;
                            const end = contentHeaderArea.current!.selectionEnd;
                            contentHeaderArea.current!.value =
                                contentHeaderArea.current!.value.substring(
                                    0,
                                    start
                                ) +
                                "\t" +
                                contentHeaderArea.current!.value.substring(end);
                            contentHeaderArea.current!.selectionStart =
                                contentHeaderArea.current!.selectionEnd =
                                    start + 1;
                        }
                    }}
                />
                <textarea
                    ref={contentTextArea}
                    className="w-4/5 h-[60vh]"
                    onKeyDown={(e) => {
                        if (e.key === "Tab") {
                            e.preventDefault();
                            const start =
                                contentTextArea.current!.selectionStart;
                            const end = contentTextArea.current!.selectionEnd;
                            contentTextArea.current!.value =
                                contentTextArea.current!.value.substring(
                                    0,
                                    start
                                ) +
                                "\t" +
                                contentTextArea.current!.value.substring(end);
                            contentTextArea.current!.selectionStart =
                                contentTextArea.current!.selectionEnd =
                                    start + 1;
                        }
                    }}
                />
                <button
                    onClick={() => {
                        if (pyodide === undefined) return;
                        pyodide.globals.set(
                            "NAMESPACE",
                            namespaceInput.current!.value
                        );
                        pyodide.globals.set(
                            "JMC_FILE",
                            contentTextArea.current!.value
                        );
                        pyodide.globals.set(
                            "HEADER_FILE",
                            contentHeaderArea.current!.value
                        );
                        pyodide.runPython(
                            `
try:
    BUILT = JMCTestPack(namespace=NAMESPACE, output=".").set_jmc_file(JMC_FILE).set_header_file(HEADER_FILE).built
except EXCEPTIONS as error:
    BUILT = {}
    ERROR = type(error).__name__ + "\\n" + str(error)`
                        );
                        const built: Map<string, string> = pyodide.globals
                            .get("BUILT")
                            .toJs();
                        if (built.size === 0) {
                            setIsError(true);
                            setJMCError(
                                pyodide.globals
                                    .get("ERROR")
                                    .replace("/home/pyodide/", "")
                            );
                        } else {
                            setIsError(false);
                            setJMCResult(built);
                        }
                    }}
                    className="w-60 h-20 text-white"
                >
                    Run
                </button>{" "}
                <div className="text-white" hidden={isError}>
                    {/* No Error */}
                    {Object.keys(Object.fromEntries(JMCResult)).map((key) => {
                        return (
                            <div key={key}>
                                <div className="bg-secondary-dark">
                                    {">"} {key}
                                </div>
                                <pre>{JMCResult.get(key)}</pre>
                            </div>
                        );
                    })}
                </div>
                <div className="text-white" hidden={!isError}>
                    {/* Error */}
                    <pre className="text-warning">{JMCError}</pre>
                </div>
            </section>
        </>
    );
};

export default TryOut;
