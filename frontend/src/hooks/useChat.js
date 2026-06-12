import { useState, useCallback } from "react";
import { sendMessage } from "../utils/api";

export function useChat() {
  const [messages, setMessages]       = useState([]);
  const [loading, setLoading]         = useState(false);
  const [profile, setProfile]         = useState(null);
  const [eligibleSchemes, setEligible] = useState([]);
  const [partialSchemes, setPartial]   = useState([]);

  const send = useCallback(async (text) => {
    const userMsg = { role: "user", content: text };
    const updatedHistory = [...messages, userMsg];
    setMessages(updatedHistory);
    setLoading(true);

    try {
      const data = await sendMessage(text, messages);
      const botMsg = { role: "assistant", content: data.reply };
      setMessages([...updatedHistory, botMsg]);

      if (data.profile_complete) {
        setProfile(data.profile);
        setEligible(data.eligible_schemes);
        setPartial(data.partial_schemes);
      }
    } catch (err) {
      setMessages([...updatedHistory, {
        role: "assistant",
        content: "Sorry, something went wrong. Please try again.",
      }]);
    } finally {
      setLoading(false);
    }
  }, [messages]);

  const reset = useCallback(() => {
    setMessages([]);
    setProfile(null);
    setEligible([]);
    setPartial([]);
  }, []);

  return { messages, loading, profile, eligibleSchemes, partialSchemes, send, reset };
}