"use client";

import type { Editor } from "@tiptap/react";
import type { ReactNode } from "react";

interface EditorToolbarProps {
  editor: Editor | null;
  onImageUpload: () => void;
}

export default function EditorToolbar({ editor, onImageUpload }: EditorToolbarProps) {
  if (!editor) return null;

  return (
    <div className="flex flex-wrap items-center gap-0.5 px-3 py-2 border-b border-warm-300/60 bg-warm-50/80 sticky top-0 z-10">
      {/* Text formatting */}
      <ToolGroup>
        <ToolBtn
          icon="format_bold"
          label="Bold"
          active={editor.isActive("bold")}
          onClick={() => editor.chain().focus().toggleBold().run()}
        />
        <ToolBtn
          icon="format_italic"
          label="Italic"
          active={editor.isActive("italic")}
          onClick={() => editor.chain().focus().toggleItalic().run()}
        />
        <ToolBtn
          icon="format_underlined"
          label="Underline"
          active={editor.isActive("underline")}
          onClick={() => editor.chain().focus().toggleUnderline().run()}
        />
        <ToolBtn
          icon="format_strikethrough"
          label="Strikethrough"
          active={editor.isActive("strike")}
          onClick={() => editor.chain().focus().toggleStrike().run()}
        />
      </ToolGroup>

      <Divider />

      {/* Headings */}
      <ToolGroup>
        <ToolBtn
          label="H1"
          text="H1"
          active={editor.isActive("heading", { level: 1 })}
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
        />
        <ToolBtn
          label="H2"
          text="H2"
          active={editor.isActive("heading", { level: 2 })}
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
        />
        <ToolBtn
          label="H3"
          text="H3"
          active={editor.isActive("heading", { level: 3 })}
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
        />
      </ToolGroup>

      <Divider />

      {/* Lists */}
      <ToolGroup>
        <ToolBtn
          icon="format_list_bulleted"
          label="Bullet list"
          active={editor.isActive("bulletList")}
          onClick={() => editor.chain().focus().toggleBulletList().run()}
        />
        <ToolBtn
          icon="format_list_numbered"
          label="Numbered list"
          active={editor.isActive("orderedList")}
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
        />
        <ToolBtn
          icon="format_quote"
          label="Blockquote"
          active={editor.isActive("blockquote")}
          onClick={() => editor.chain().focus().toggleBlockquote().run()}
        />
        <ToolBtn
          icon="code"
          label="Code block"
          active={editor.isActive("codeBlock")}
          onClick={() => editor.chain().focus().toggleCodeBlock().run()}
        />
      </ToolGroup>

      <Divider />

      {/* Alignment */}
      <ToolGroup>
        <ToolBtn
          icon="format_align_left"
          label="Align left"
          active={editor.isActive({ textAlign: "left" })}
          onClick={() => editor.chain().focus().setTextAlign("left").run()}
        />
        <ToolBtn
          icon="format_align_center"
          label="Align center"
          active={editor.isActive({ textAlign: "center" })}
          onClick={() => editor.chain().focus().setTextAlign("center").run()}
        />
        <ToolBtn
          icon="format_align_right"
          label="Align right"
          active={editor.isActive({ textAlign: "right" })}
          onClick={() => editor.chain().focus().setTextAlign("right").run()}
        />
      </ToolGroup>

      <Divider />

      {/* Media */}
      <ToolGroup>
        <ToolBtn
          icon="image"
          label="Insert image"
          onClick={onImageUpload}
        />
      </ToolGroup>

      {/* Undo / Redo */}
      <div className="ml-auto flex items-center gap-0.5">
        <ToolBtn
          icon="undo"
          label="Undo"
          onClick={() => editor.chain().focus().undo().run()}
          disabled={!editor.can().undo()}
        />
        <ToolBtn
          icon="redo"
          label="Redo"
          onClick={() => editor.chain().focus().redo().run()}
          disabled={!editor.can().redo()}
        />
      </div>
    </div>
  );
}

function ToolGroup({ children }: { children: ReactNode }) {
  return <div className="flex items-center gap-0.5">{children}</div>;
}

function Divider() {
  return <div className="w-px h-5 bg-warm-300 mx-1" />;
}

function ToolBtn({
  icon,
  text,
  label,
  active,
  onClick,
  disabled,
}: {
  icon?: string;
  text?: string;
  label: string;
  active?: boolean;
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      title={label}
      onClick={onClick}
      disabled={disabled}
      className={`
        h-8 min-w-[32px] px-1.5 flex items-center justify-center rounded-lg text-sm
        transition-all duration-100 font-medium
        ${
          active
            ? "bg-primary/10 text-primary"
            : "text-slate-400 hover:bg-warm-200 hover:text-slate-600"
        }
        ${disabled ? "opacity-30 cursor-not-allowed" : ""}
      `}
    >
      {icon ? (
        <span className="material-symbols-outlined text-[18px]">{icon}</span>
      ) : (
        <span className="text-xs leading-none">{text}</span>
      )}
    </button>
  );
}
