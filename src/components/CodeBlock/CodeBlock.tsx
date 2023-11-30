import React from "react";
import "./CodeBlock.css";

interface Code {
    copy_text?: string;
    children?: React.ReactNode;
}

const CodeBlock: React.FC<Code> = (props) => {
    return (
        <>
            <div className="relative my-2 md:my-4 bg-[#292D3E] rounded-md md:rounded-2xl text-[#eeffff] px-4 py-1 md:px-8 md:py-3">
                <div className="font-monocraft m-0 p-0 pb-2 text-xs md:text-2xl overflow-y-auto whitespace-nowrap">
                    {props.children}
                </div>
            </div>
        </>
    );
};

interface Text {
    type: string;
    children: React.ReactNode;
}

const CodeText: React.FC<Text> = (props) => {
    return (
        <span className={"code-text inline-block color-" + props.type}>
            {props.children}
        </span>
    );
};

interface CommandInterface {
    name: string;
    type: string;
    params: Array<Parameter>;
    newline?: boolean;
}
interface Parameter {
    key: string;
    type: string;
    default?: string;
}

const getDefault = (param: Parameter) => {
    if (
        param.default === "()=>{}" &&
        (param.type === "Function" || param.type === "ArrowFunction")
    ) {
        return (
            <>
                {"()"}
                <CodeText type="keyword">{"=>"}</CodeText>
                {"{}"}
            </>
        );
    }

    let type;
    switch (param.type) {
        case "integer":
            type = "number";
            break;
        case "float":
            type = "number";
            break;
        case "TargetSelector":
            type = "param";
            break;
        case "boolean":
            type = "operator";
            break;
        case "FormattedString":
            type = "string";
            break;
        default:
            type = param.type;
    }

    return <CodeText type={type}>{param.default}</CodeText>;
};

const Command: React.FC<CommandInterface> = (props) => {
    const module_function = props.name.split(".");
    const module_name = module_function[0];
    const function_name =
        module_function.length === 2 ? module_function[1] : null;
    const len = props.params.length;
    const copy_text = `${module_name}.${function_name}(${props.params.map(
        (param, index) => `
        ${param.key}: ${param.type}${
            param.default !== undefined ? ` = ${param.default}` : ""
        }${index !== len - 1 ? ", " : ""}
    `
    )})`;
    return (
        <CodeBlock copy_text={copy_text}>
            {function_name === null ? (
                <CodeText type="function">{module_function}</CodeText>
            ) : (
                <>
                    <CodeText type="class">{module_name}</CodeText>
                    <CodeText type="operator">.</CodeText>
                    <CodeText type="function">{function_name}</CodeText>
                </>
            )}
            (
            {props.newline && (
                <>
                    <br />
                    <Tab />
                </>
            )}
            {props.params.map((param, index) => (
                <span key={index}>
                    {param.key}
                    <CodeText type="operator">:</CodeText>{" "}
                    <CodeText type="class">{param.type}</CodeText>
                    {param.default !== undefined ? (
                        <>
                            {" "}
                            <CodeText type="operator">=</CodeText>{" "}
                            {getDefault(param)}
                        </>
                    ) : (
                        ""
                    )}
                    {index !== len - 1 ? (
                        props.newline ? (
                            <>
                                <CodeText type="operator">,</CodeText>
                                <br />
                                <Tab />
                            </>
                        ) : (
                            <CodeText type="operator">,&nbsp;</CodeText>
                        )
                    ) : (
                        ""
                    )}
                </span>
            ))}
            {props.newline && <br />}){" "}
            <CodeText type="operator">{"->"}</CodeText>{" "}
            <CodeText type="class">{props.type}</CodeText>
        </CodeBlock>
    );
};

Command.defaultProps = {
    newline: false,
};

const Tab: React.FC = () => {
    return <>&nbsp;&nbsp;&nbsp;&nbsp;</>;
};

export { CodeText, Command, Tab };
export default CodeBlock;
