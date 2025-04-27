declare global {
    interface Window {
        loadPyodide: (config: {
            indexURL: string;
        }) => Promise<PyodideInterface>;
    }
}
export interface PyodideInterface {
    runPython: (code: string) => any;
    runPythonAsync: (code: string) => Promise<any>;
    loadPackage: (packageName: string | string[]) => Promise<void>;
    pyimport: (moduleName: string) => any;
    globals: {
        get: (key: string) => any;
        set: (key: string, value: any) => void;
    };
}
