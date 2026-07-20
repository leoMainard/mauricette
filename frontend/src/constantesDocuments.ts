/**
 * Extensions de fichiers acceptées lors du dépôt de documents, en miroir de
 * `EXTENSIONS_SUPPORTEES` côté backend (`infrastructure/rag/docling_adapter.py`).
 * Sert d'indication pour le sélecteur de fichiers du navigateur : le serveur
 * reste seul juge final (un glisser-déposer ou un "Tous les fichiers" peut
 * toujours contourner cette liste).
 */
export const EXTENSIONS_DOCUMENTS_ACCEPTEES = [
  ".pdf",
  ".docx",
  ".dotx",
  ".docm",
  ".dotm",
  ".xlsx",
  ".xlsm",
  ".pptx",
  ".potx",
  ".ppsx",
  ".pptm",
  ".potm",
  ".ppsm",
  ".odt",
  ".ott",
  ".ods",
  ".ots",
  ".odp",
  ".otp",
  ".html",
  ".htm",
  ".xhtml",
  ".md",
  ".txt",
  ".csv",
  ".epub",
  ".jpg",
  ".jpeg",
  ".png",
  ".tif",
  ".tiff",
  ".bmp",
  ".webp",
  ".zip",
].join(",");
