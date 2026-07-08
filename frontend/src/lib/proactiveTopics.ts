import type {
  RoleCueMessage,
  TopicMaterialContext,
} from "@/types/chat";
import type { MemoryEntry } from "@/types/memory";
import { TOPIC_CARDS } from "@/lib/topicCards";

export interface ProactiveTopic {
  id: string;
  label: string;
  cue: string;
}

export interface AmbientChatScene {
  id: string;
  sourceLabel: string;
  headline: string;
  interestAnchor: string;
  topic: TopicMaterialContext;
  joinMessage: string;
  roleMessages: RoleCueMessage[];
  keywords: string[];
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

const topicById = new Map(TOPIC_CARDS.map((topic) => [topic.topic_id, topic]));

function topic(id: string): TopicMaterialContext {
  const found = topicById.get(id);
  if (!found) {
    throw new Error(`Missing topic card ${id}`);
  }
  return found;
}

const AMBIENT_SCENES: AmbientChatScene[] = [
  {
    id: "opera_local_culture",
    sourceLabel: "今日话题",
    headline: "最近不少社区活动又把老歌、戏曲和地方文化摆上台面。",
    interestAnchor: "听到这些，我想到您可能会对熟悉的唱腔有感觉。",
    topic: topic("T06"),
    joinMessage: "我想加入你们刚才聊的戏曲和地方文化话题。",
    keywords: ["粤剧", "戏曲", "老歌", "唱歌", "音乐", "地方文化", "电影"],
    roleMessages: [
      {
        role_id: "theme_companion",
        role_label: "主题陪伴者",
        text: "说到最近大家聊的地方文化，我一下想到粤剧和老戏，老腔老调里常有一个年代的味道。",
      },
      {
        role_id: "same_age_peer",
        role_label: "同龄共鸣者",
        text: "是啊，有些唱段一响起来，人就会想起从前在哪儿听、和谁一起听。",
      },
      {
        role_id: "curious_junior",
        role_label: "晚辈好奇者",
        text: "您要是愿意进来，也可以说说最熟的一段，或者哪一句最有味道。",
      },
    ],
  },
  {
    id: "neighborhood_walk",
    sourceLabel: "今日话题",
    headline: "最近大家常聊出门走走、社区活动和怎么舒服地过一天。",
    interestAnchor: "这个话题可以从日常路上看到的小变化说起。",
    topic: topic("T04"),
    joinMessage: "我想加入你们刚才聊的邻里和社区日常话题。",
    keywords: ["散步", "走路", "社区", "邻居", "公园", "买菜", "活动"],
    roleMessages: [
      {
        role_id: "theme_companion",
        role_label: "主题陪伴者",
        text: "最近不少人会聊社区里有什么新变化，哪条路好走，哪里坐一会儿舒服。",
      },
      {
        role_id: "same_age_peer",
        role_label: "同龄共鸣者",
        text: "这些小地方很实在，熟悉的邻里和路口，常常比大新闻更贴近日子。",
      },
      {
        role_id: "curious_junior",
        role_label: "晚辈好奇者",
        text: "您如果刚好想聊，也可以说说最近常去哪里，或者哪条路最顺脚。",
      },
    ],
  },
  {
    id: "old_photo_memory",
    sourceLabel: "今日话题",
    headline: "最近很多人会把旧照片、旧物件拿出来，重新讲一讲背后的故事。",
    interestAnchor: "这样的开场不急着追问，只从一个物件慢慢聊。",
    topic: topic("T05"),
    joinMessage: "我想加入你们刚才聊的旧照片和旧物件话题。",
    keywords: ["照片", "相册", "旧物", "老物件", "纪念", "以前", "从前"],
    roleMessages: [
      {
        role_id: "theme_companion",
        role_label: "主题陪伴者",
        text: "一张旧照片有时候不只是照片，还藏着当时的天气、衣服、地方和人情。",
      },
      {
        role_id: "same_age_peer",
        role_label: "同龄共鸣者",
        text: "我也觉得，旧物件一拿起来，很多细节会自己慢慢回来。",
      },
      {
        role_id: "curious_junior",
        role_label: "晚辈好奇者",
        text: "您如果愿意加入，可以先从一个记得最清楚的画面说起。",
      },
    ],
  },
  {
    id: "new_life_technology",
    sourceLabel: "今日话题",
    headline: "最近新技术和生活服务变化很快，很多人会拿它和从前的生活比较。",
    interestAnchor: "这个话题适合听您评价哪些变化方便，哪些反而麻烦。",
    topic: topic("T11"),
    joinMessage: "我想加入你们刚才聊的新技术和生活变化话题。",
    keywords: ["手机", "科技", "技术", "电视", "支付", "智能", "新生活"],
    roleMessages: [
      {
        role_id: "theme_companion",
        role_label: "主题陪伴者",
        text: "现在很多服务都搬到手机上，有些确实方便，有些也让人觉得太绕。",
      },
      {
        role_id: "same_age_peer",
        role_label: "同龄共鸣者",
        text: "变化太快的时候，最重要的是别被催着走，按自己舒服的速度来。",
      },
      {
        role_id: "curious_junior",
        role_label: "晚辈好奇者",
        text: "您要是愿意，也可以进来讲讲哪件新东西好用，哪件不太顺手。",
      },
    ],
  },
  {
    id: "seasonal_everyday",
    sourceLabel: "今日话题",
    headline: "最近大家也会聊节气、饮食和一天里让人舒服的小安排。",
    interestAnchor: "没有特定兴趣时，可以从轻松的时令日常开始。",
    topic: topic("T12"),
    joinMessage: "我想加入你们刚才聊的时令和日常心情话题。",
    keywords: ["天气", "节气", "吃饭", "喝茶", "休息", "日常", "心情"],
    roleMessages: [
      {
        role_id: "theme_companion",
        role_label: "主题陪伴者",
        text: "说到时令日常，有时就是一杯茶、一顿顺口的饭，或者一天里最安静的一小段。",
      },
      {
        role_id: "same_age_peer",
        role_label: "同龄共鸣者",
        text: "日子不一定要讲得很大，舒服不舒服，往往就在这些小安排里。",
      },
      {
        role_id: "curious_junior",
        role_label: "晚辈好奇者",
        text: "您若想加入，可以说说今天哪一刻最踏实，或者想换个轻松话题也行。",
      },
    ],
  },
];

function scoreScene(scene: AmbientChatScene, memoryText: string): number {
  if (!memoryText) return scene.id === "opera_local_culture" ? 1 : 0;
  return scene.keywords.reduce(
    (score, keyword) => score + (memoryText.includes(keyword) ? 3 : 0),
    scene.id === "seasonal_everyday" ? 1 : 0,
  );
}

export function buildAmbientChatScenes(
  memories: MemoryEntry[],
): AmbientChatScene[] {
  const memoryText = memories.map((memory) => memory.content).join(" ");
  return [...AMBIENT_SCENES].sort(
    (a, b) => scoreScene(b, memoryText) - scoreScene(a, memoryText),
  );
}
