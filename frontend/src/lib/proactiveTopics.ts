export interface ProactiveTopic {
  id: string;
  label: string;
  cue: string;
}

export const PROACTIVE_TOPIC_BANK: ProactiveTopic[] = [
  {
    id: "weather_walk",
    label: "天气与散步",
    cue: "天气合适时，温和邀请用户看看是否想短短走一会儿。",
  },
  {
    id: "old_photo",
    label: "旧照片或旧物",
    cue: "从用户愿意分享的照片、旧物或生活片段自然开启回忆。",
  },
  {
    id: "music_opera",
    label: "音乐与戏曲",
    cue: "围绕喜欢的老歌、粤剧或戏曲片段轻轻聊两句。",
  },
  {
    id: "family_friends",
    label: "家人朋友近况",
    cue: "只在用户愿意时聊近况，不替代家人或编造关系信息。",
  },
  {
    id: "festival_season",
    label: "节日与时令",
    cue: "用节气、节日或社区活动作为低压力开场。",
  },
  {
    id: "light_movement",
    label: "轻量活动",
    cue: "提醒伸展、站起来走两步或休息一下，不做健康判断。",
  },
  {
    id: "hydration_rest",
    label: "喝水与休息",
    cue: "在合适时间做生活化提醒，避免频繁打扰。",
  },
];
