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
            ]}
        />,
    ];
};

export default getDocsPages;
