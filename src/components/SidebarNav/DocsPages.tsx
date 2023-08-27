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
            keyword=""
            page="import"
            searchValue={searchValue}
        />,
        <DocsLink
            name="Comment"
            keyword=""
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
                    keyword=""
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
            ]}
        />,
    ];
};

export default getDocsPages;
