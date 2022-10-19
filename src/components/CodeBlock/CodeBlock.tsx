import React from 'react'
import "./CodeBlock.css";

interface Code {
    copy_text: string
    children: React.ReactNode
}

const CodeBlock: React.FC<Code> = (props) => {
    return <>
        <div className='relative my-4 bg-[#292D3E] rounded-md md:rounded-2xl text-[#eeffff] px-4 py-1 md:px-8 md:py-3'>
            <div className='m-0 p-0 pb-2 text-sm md:text-2xl overflow-y-auto whitespace-nowrap'>{props.children}</div>
        </div>
    </>
}

interface Text {
    type: string
    children: React.ReactNode
}

const CodeText: React.FC<Text> = (props) => {
    return <p className={'code-text inline-block color-' + props.type}>{props.children}</p>
}

interface CommandInterface {
    name: string,
    type: string,
    params: Array<Parameter>
}
interface Parameter {
    key: string,
    type: string,
    default?: string
}
const Command: React.FC<CommandInterface> = (props) => {
    const module_function = props.name.split('.')
    const module_name = module_function[0]
    const function_name = module_function[1]
    const len = props.params.length
    const copy_text = `${module_name}.${function_name}(${props.params.map((param, index) => (`
        ${param.key}: ${param.type}${param.default !== undefined ? ` = ${param.default}` : ""}${index !== len - 1 ? ", " : ""}
    `))})`
    return <CodeBlock copy_text={copy_text}>
        <CodeText type="class">{module_name}</CodeText><CodeText type="operator">.</CodeText><CodeText type="function">{function_name}</CodeText>({
            props.params.map((param, index) => (
                <>{param.key}<CodeText type="operator">:&nbsp;</CodeText><CodeText type="class">{param.type}</CodeText>{param.default !== undefined ? <><CodeText type="operator">&nbsp;=&nbsp;</CodeText><CodeText type={param.type}>{param.default}</CodeText></> : ""}{index !== len - 1 ? <CodeText type="operator">,&nbsp;</CodeText> : ""}</>
            ))
        })<CodeText type="operator">&nbsp;{"->"}&nbsp;</CodeText><CodeText type="class">LoadOnly</CodeText>
    </CodeBlock>
}

export { CodeText, Command }
export default CodeBlock
