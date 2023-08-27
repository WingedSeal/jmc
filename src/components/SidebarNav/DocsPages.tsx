import React, { ReactElement } from "react";
import DocsLink, { DocsLinkInterface } from "./DocsLink";

const getDocsPages = (
    searchValue: string
): ReactElement<DocsLinkInterface>[] => {
    return [
        <DocsLink
            name="Multiline Command"
            keyword=""
            page="multiline-command"
            searchValue={searchValue}
        />,
        <DocsLink
            name="Import"
            keyword="include copy"
            page="import"
            searchValue={searchValue}
        />,
        <DocsLink
            name="Comment"
            keyword="comments // #"
            page="comment"
            searchValue={searchValue}
        />,
        <DocsLink
            name="Function"
            keyword=""
            page="function"
            searchValue={searchValue}
            sections={[
                <DocsLink
                    name="Function defining"
                    keyword="define"
                    page="function"
                    hash="function_defining"
                    searchValue={searchValue}
                />,
                <DocsLink
                    name="Function calling"
                    keyword=""
                    page="function"
                    hash="function_calling"
                    searchValue={searchValue}
                />,
                <DocsLink
                    name="Anonymous Function"
                    keyword="arrow hidden execute"
                    page="function"
                    hash="anonymous_function"
                    searchValue={searchValue}
                />,
                <DocsLink
                    name="Execute Expand"
                    keyword="copy paste hardcode"
                    page="function"
                    hash="execute_expand"
                    searchValue={searchValue}
                />,
                <DocsLink
                    name="Class"
                    keyword="grouping layer folder"
                    page="function"
                    hash="class"
                    searchValue={searchValue}
                />,
            ]}
        />,
        <DocsLink
            name="Load/Tick"
            keyword="loop main json"
            page="load-tick"
            searchValue={searchValue}
        />,
        <DocsLink
            name="Variable"
            keyword="loop main json"
            page="variable"
            searchValue={searchValue}
            sections={[
                <DocsLink
                    name="Variable Assignment"
                    keyword="= equal set initialize"
                    page="variable"
                    hash="variable_assignment"
                    searchValue={searchValue}
                />,
                <DocsLink
                    name="Variable Operation"
                    keyword="+=-=*=/=%=><??= null coalescing coalesce maximum minimum operator add subtract modulus division divide assignment set swap"
                    page="variable"
                    hash="variable_operation"
                    searchValue={searchValue}
                />,
                <DocsLink
                    name="Incrementation"
                    keyword="decrementation"
                    page="variable"
                    hash="decrementation"
                    searchValue={searchValue}
                />,
                <DocsLink
                    name="Get variable"
                    keyword="nbt"
                    page="variable"
                    hash="get_variable"
                    searchValue={searchValue}
                />,
                <DocsLink
                    name="Convert to string"
                    keyword="formatted toString"
                    page="variable"
                    hash="convert_to_string"
                    searchValue={searchValue}
                />,
                <DocsLink
                    name="Execute Store"
                    keyword="?= result success nbt"
                    page="variable"
                    hash="execute_store"
                    searchValue={searchValue}
                />,
            ]}
        />,
        <DocsLink
            name="Flow Controls"
            keyword=""
            page="flow-controls"
            searchValue={searchValue}
            sections={[
                <DocsLink
                    name="Condition"
                    keyword=">= <= === matches if"
                    page="flow-controls"
                    searchValue={searchValue}
                    hash="condition"
                />,
            ]}
        />,
    ];
};

export default getDocsPages;
