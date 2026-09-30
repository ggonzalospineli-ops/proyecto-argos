-- CreateEnum
CREATE TYPE "UserRole" AS ENUM ('ADMIN', 'MEMBER', 'VIEWER');

-- CreateEnum
CREATE TYPE "ProjectStatus" AS ENUM ('ACTIVE', 'ARCHIVED');

-- CreateEnum
CREATE TYPE "EntityStatus" AS ENUM ('ACTIVE', 'DEPRECATED');

-- CreateEnum
CREATE TYPE "ComponentType" AS ENUM ('HARDWARE', 'SOFTWARE', 'ASSEMBLY');

-- CreateEnum
CREATE TYPE "ComponentStatus" AS ENUM ('DRAFT', 'DESIGN', 'PROTOTYPE', 'TESTING', 'VALIDATED', 'RELEASED', 'DEPRECATED');

-- CreateEnum
CREATE TYPE "RevisionStatus" AS ENUM ('DRAFT', 'RELEASED', 'DEPRECATED');

-- CreateEnum
CREATE TYPE "DocumentEntityType" AS ENUM ('SYSTEM', 'COMPONENT', 'REVISION', 'BUILD', 'TEST');

-- CreateEnum
CREATE TYPE "DocumentStatus" AS ENUM ('DRAFT', 'PUBLISHED');

-- CreateEnum
CREATE TYPE "DependencyType" AS ENUM ('DEPENDS_ON', 'CONTAINS', 'COMPATIBLE_WITH');

-- CreateEnum
CREATE TYPE "BuildStatus" AS ENUM ('PLANNED', 'ASSEMBLED', 'TESTING', 'ARCHIVED');

-- CreateEnum
CREATE TYPE "TestResult" AS ENUM ('PASS', 'FAIL', 'INCONCLUSIVE');

-- CreateTable
CREATE TABLE "users" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "password_hash" TEXT NOT NULL,
    "role" "UserRole" NOT NULL DEFAULT 'MEMBER',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "projects" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "status" "ProjectStatus" NOT NULL DEFAULT 'ACTIVE',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "projects_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "systems" (
    "id" TEXT NOT NULL,
    "project_id" TEXT NOT NULL,
    "parent_system_id" TEXT,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "status" "EntityStatus" NOT NULL DEFAULT 'ACTIVE',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "systems_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "components" (
    "id" TEXT NOT NULL,
    "project_id" TEXT NOT NULL,
    "parent_system_id" TEXT,
    "parent_component_id" TEXT,
    "name" TEXT NOT NULL,
    "type" "ComponentType" NOT NULL,
    "description" TEXT,
    "status" "ComponentStatus" NOT NULL DEFAULT 'DRAFT',
    "current_revision_id" TEXT,
    "owner_id" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "components_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "revisions" (
    "id" TEXT NOT NULL,
    "component_id" TEXT NOT NULL,
    "label" TEXT NOT NULL,
    "status" "RevisionStatus" NOT NULL DEFAULT 'DRAFT',
    "description" TEXT,
    "change_summary" TEXT,
    "author_id" TEXT NOT NULL,
    "previous_revision_id" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "revisions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "artifacts" (
    "id" TEXT NOT NULL,
    "revision_id" TEXT NOT NULL,
    "filename" TEXT NOT NULL,
    "file_type" TEXT NOT NULL,
    "size_bytes" BIGINT NOT NULL,
    "checksum" TEXT NOT NULL,
    "storage_key" TEXT NOT NULL,
    "uploaded_by" TEXT NOT NULL,
    "uploaded_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "artifacts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "documents" (
    "id" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "content_markdown" TEXT NOT NULL,
    "entity_type" "DocumentEntityType" NOT NULL,
    "entity_id" TEXT NOT NULL,
    "status" "DocumentStatus" NOT NULL DEFAULT 'DRAFT',
    "author_id" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "documents_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "component_dependencies" (
    "id" TEXT NOT NULL,
    "from_component_id" TEXT NOT NULL,
    "to_component_id" TEXT NOT NULL,
    "type" "DependencyType" NOT NULL,
    "notes" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "component_dependencies_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "bom_lines" (
    "id" TEXT NOT NULL,
    "parent_component_id" TEXT NOT NULL,
    "child_component_id" TEXT NOT NULL,
    "quantity" INTEGER NOT NULL DEFAULT 1,
    "child_revision_id" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "bom_lines_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "builds" (
    "id" TEXT NOT NULL,
    "project_id" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "description" TEXT,
    "status" "BuildStatus" NOT NULL DEFAULT 'PLANNED',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "builds_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "build_components" (
    "id" TEXT NOT NULL,
    "build_id" TEXT NOT NULL,
    "component_id" TEXT NOT NULL,
    "revision_id" TEXT NOT NULL,

    CONSTRAINT "build_components_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "tests" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "target_component_id" TEXT NOT NULL,
    "build_id" TEXT,
    "description" TEXT,
    "result" "TestResult" NOT NULL DEFAULT 'INCONCLUSIVE',
    "notes" TEXT,
    "date" TIMESTAMP(3) NOT NULL,
    "created_by" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "tests_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- CreateIndex
CREATE INDEX "systems_project_id_idx" ON "systems"("project_id");

-- CreateIndex
CREATE INDEX "systems_parent_system_id_idx" ON "systems"("parent_system_id");

-- CreateIndex
CREATE UNIQUE INDEX "components_current_revision_id_key" ON "components"("current_revision_id");

-- CreateIndex
CREATE INDEX "components_project_id_idx" ON "components"("project_id");

-- CreateIndex
CREATE INDEX "components_parent_system_id_idx" ON "components"("parent_system_id");

-- CreateIndex
CREATE INDEX "components_parent_component_id_idx" ON "components"("parent_component_id");

-- CreateIndex
CREATE INDEX "revisions_component_id_idx" ON "revisions"("component_id");

-- CreateIndex
CREATE UNIQUE INDEX "revisions_component_id_label_key" ON "revisions"("component_id", "label");

-- CreateIndex
CREATE INDEX "artifacts_revision_id_idx" ON "artifacts"("revision_id");

-- CreateIndex
CREATE INDEX "documents_entity_type_entity_id_idx" ON "documents"("entity_type", "entity_id");

-- CreateIndex
CREATE INDEX "component_dependencies_from_component_id_idx" ON "component_dependencies"("from_component_id");

-- CreateIndex
CREATE INDEX "component_dependencies_to_component_id_idx" ON "component_dependencies"("to_component_id");

-- CreateIndex
CREATE UNIQUE INDEX "component_dependencies_from_component_id_to_component_id_ty_key" ON "component_dependencies"("from_component_id", "to_component_id", "type");

-- CreateIndex
CREATE UNIQUE INDEX "bom_lines_parent_component_id_child_component_id_key" ON "bom_lines"("parent_component_id", "child_component_id");

-- CreateIndex
CREATE UNIQUE INDEX "builds_project_id_code_key" ON "builds"("project_id", "code");

-- CreateIndex
CREATE INDEX "build_components_build_id_idx" ON "build_components"("build_id");

-- CreateIndex
CREATE INDEX "build_components_component_id_idx" ON "build_components"("component_id");

-- CreateIndex
CREATE UNIQUE INDEX "build_components_build_id_component_id_key" ON "build_components"("build_id", "component_id");

-- CreateIndex
CREATE INDEX "tests_target_component_id_idx" ON "tests"("target_component_id");

-- CreateIndex
CREATE INDEX "tests_build_id_idx" ON "tests"("build_id");

-- AddForeignKey
ALTER TABLE "systems" ADD CONSTRAINT "systems_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "projects"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "systems" ADD CONSTRAINT "systems_parent_system_id_fkey" FOREIGN KEY ("parent_system_id") REFERENCES "systems"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "components" ADD CONSTRAINT "components_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "projects"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "components" ADD CONSTRAINT "components_parent_system_id_fkey" FOREIGN KEY ("parent_system_id") REFERENCES "systems"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "components" ADD CONSTRAINT "components_parent_component_id_fkey" FOREIGN KEY ("parent_component_id") REFERENCES "components"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "components" ADD CONSTRAINT "components_current_revision_id_fkey" FOREIGN KEY ("current_revision_id") REFERENCES "revisions"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "revisions" ADD CONSTRAINT "revisions_component_id_fkey" FOREIGN KEY ("component_id") REFERENCES "components"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "revisions" ADD CONSTRAINT "revisions_author_id_fkey" FOREIGN KEY ("author_id") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "revisions" ADD CONSTRAINT "revisions_previous_revision_id_fkey" FOREIGN KEY ("previous_revision_id") REFERENCES "revisions"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "artifacts" ADD CONSTRAINT "artifacts_revision_id_fkey" FOREIGN KEY ("revision_id") REFERENCES "revisions"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "artifacts" ADD CONSTRAINT "artifacts_uploaded_by_fkey" FOREIGN KEY ("uploaded_by") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "documents" ADD CONSTRAINT "documents_author_id_fkey" FOREIGN KEY ("author_id") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "component_dependencies" ADD CONSTRAINT "component_dependencies_from_component_id_fkey" FOREIGN KEY ("from_component_id") REFERENCES "components"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "component_dependencies" ADD CONSTRAINT "component_dependencies_to_component_id_fkey" FOREIGN KEY ("to_component_id") REFERENCES "components"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "bom_lines" ADD CONSTRAINT "bom_lines_parent_component_id_fkey" FOREIGN KEY ("parent_component_id") REFERENCES "components"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "bom_lines" ADD CONSTRAINT "bom_lines_child_component_id_fkey" FOREIGN KEY ("child_component_id") REFERENCES "components"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "builds" ADD CONSTRAINT "builds_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "projects"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "build_components" ADD CONSTRAINT "build_components_build_id_fkey" FOREIGN KEY ("build_id") REFERENCES "builds"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "build_components" ADD CONSTRAINT "build_components_component_id_fkey" FOREIGN KEY ("component_id") REFERENCES "components"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "build_components" ADD CONSTRAINT "build_components_revision_id_fkey" FOREIGN KEY ("revision_id") REFERENCES "revisions"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "tests" ADD CONSTRAINT "tests_target_component_id_fkey" FOREIGN KEY ("target_component_id") REFERENCES "components"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "tests" ADD CONSTRAINT "tests_build_id_fkey" FOREIGN KEY ("build_id") REFERENCES "builds"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "tests" ADD CONSTRAINT "tests_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
