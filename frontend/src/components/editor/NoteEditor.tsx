"use client";

import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Image from "@tiptap/extension-image";
import Placeholder from "@tiptap/extension-placeholder";
import Underline from "@tiptap/extension-underline";
import TextAlign from "@tiptap/extension-text-align";
import Highlight from "@tiptap/extension-highlight";
import Link from "@tiptap/extension-link";
import { useCallback, useRef } from "react";
import EditorToolbar from "./EditorToolbar";
import { uploadImage } from "@/lib/api/upload";

interface NoteEditorProps {
  content?: string;
  onChange?: (json: string) => void;
  noteId?: string;
}

export default function NoteEditor({ content, onChange, noteId }: NoteEditorProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const editor = useEditor({
    extensions: [
      StarterKit,
      Image.configure({ inline: false, allowBase64: true }),
      Placeholder.configure({
        placeholder: "Start writing… or paste content here.",
      }),
      Underline,
      TextAlign.configure({ types: ["heading", "paragraph"] }),
      Highlight,
      Link.configure({ openOnClick: false }),
    ],
    content: (() => {
      if (!content) return "";
      try {
        return JSON.parse(content);
      } catch {
        return content;
      }
    })(),
    onUpdate: ({ editor }) => {
      onChange?.(JSON.stringify(editor.getJSON()));
    },
    editorProps: {
      attributes: {
        class: "tiptap-editor px-8 py-6 min-h-[60vh] focus:outline-none",
      },
    },
    immediatelyRender: false, // ⚠️ important for SSR
  });

  const handleImageUpload = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleFileChange = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file || !editor) return;

      // Preview immediately with base64
      const reader = new FileReader();
      reader.onload = (ev) => {
        const dataUrl = ev.target?.result as string;
        editor.chain().focus().setImage({ src: dataUrl }).run();
      };
      reader.readAsDataURL(file);

      // TODO: BACKEND — uploadImage calls POST /api/upload/image
      // When backend returns the hosted image URL and extracted text,
      // replace the base64 src with the real URL and insert extracted text below.
      try {
        const fd = new FormData();
        fd.append("image", file);
        if (noteId) fd.append("note_id", noteId);
        const result = await uploadImage(fd);
        // Insert extracted text as a paragraph after the image
        if (result.extracted_text && !result.extracted_text.includes("[Mock]")) {
          editor
            .chain()
            .focus()
            .insertContent({
              type: "paragraph",
              content: [{ type: "text", text: `📝 ${result.extracted_text}` }],
            })
            .run();
        }
      } catch (err) {
        console.error("Image upload failed:", err);
      }

      if (fileInputRef.current) fileInputRef.current.value = "";
    },
    [editor, noteId]
  );

  return (
    <div className="flex flex-col rounded-2xl border border-warm-400/60 bg-white overflow-hidden shadow-warm-sm">
      <EditorToolbar editor={editor} onImageUpload={handleImageUpload} />
      <EditorContent editor={editor} />
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleFileChange}
      />
    </div>
  );
}
