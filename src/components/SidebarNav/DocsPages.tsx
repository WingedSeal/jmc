import DocsLink from "./DocsLink";

const DocsPages = [
    <DocsLink name="Multiline Command" keyword="" page="multiline-command" />,
    <DocsLink name="Import" keyword="" page="import" />,
    <DocsLink name="Comment" keyword="" page="comment" />,
    <DocsLink
        name="Function"
        keyword=""
        page="function"
        sections={[
            <DocsLink
                name="Function defining"
                keyword=""
                page="function"
                hash="function_defining"
            />,
        ]}
    />,
];

export default DocsPages;
