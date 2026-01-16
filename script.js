// 替换为你的飞书多维表格 JSON 公开链接
const FEISHU_TABLE_URL = "https://www.feishu.cn/drive/api/explore/open_api/v1/...";

/**
 * 请求飞书表格数据（处理跨域：使用免费 CORS 代理，生产环境可自建）
 */
async function fetchFeishuData() {
  try {
    // 解决跨域问题：飞书接口默认不允许跨域，需通过 CORS 代理转发
    const proxyUrl = "https://cors-anywhere.herokuapp.com/";
    const response = await fetch(`${proxyUrl}${FEISHU_TABLE_URL}`);
    
    if (!response.ok) throw new Error("数据请求失败");
    const data = await response.json();
    
    // 过滤出已发布的文章，并按发布时间倒序排序
    const publishedPosts = data.data.items
      .filter(item => item["是否发布"]) // 匹配表格中的「是否发布」字段
      .sort((a, b) => new Date(b["发布时间"]) - new Date(a["发布时间"]));
    
    return publishedPosts;
  } catch (error) {
    console.error("获取博客数据失败：", error);
    return [];
  }
}

/**
 * 渲染首页文章列表
 */
async function renderPostList() {
  const posts = await fetchFeishuData();
  const listEl = document.querySelector(".post-list");
  
  if (posts.length === 0) {
    listEl.innerHTML = "<p>暂无已发布的博客文章</p>";
    return;
  }
  
  // 遍历生成文章列表
  posts.forEach(post => {
    const tags = post["标签"]?.map(tag => `<span class="tag">${tag}</span>`).join("") || "";
    const postItem = `
      <div class="post-item">
        <h2><a href="post.html?slug=${post.Slug}">${post.标题}</a></h2>
        <div class="post-meta">
          ${new Date(post["发布时间"]).toLocaleDateString()} · ${tags}
        </div>
        <p>${post.正文.substring(0, 100)}...</p>
      </div>
    `;
    listEl.innerHTML += postItem;
  });
}

/**
 * 渲染博客详情页
 */
async function renderPostDetail() {
  // 从 URL 获取 Slug 参数
  const urlParams = new URLSearchParams(window.location.search);
  const slug = urlParams.get("slug");
  if (!slug) {
    document.querySelector(".post-detail").innerHTML = "<p>文章不存在</p>";
    return;
  }

  const posts = await fetchFeishuData();
  const post = posts.find(item => item.Slug === slug);
  
  if (!post) {
    document.querySelector(".post-detail").innerHTML = "<p>文章不存在</p>";
    return;
  }

  const tags = post["标签"]?.map(tag => `<span class="tag">${tag}</span>`).join("") || "";
  const postDetail = `
    <h1>${post.标题}</h1>
    <div class="post-meta">
      ${new Date(post["发布时间"]).toLocaleDateString()} · ${tags}
    </div>
    <div class="post-content">${post.正文}</div>
  `;
  document.querySelector(".post-detail").innerHTML = postDetail;
}
